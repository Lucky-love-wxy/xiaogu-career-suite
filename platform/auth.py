"""登录：手机号 / 邮箱 + 验证码；新用户首次登录必须带邀请码。

验证码怎么发出去由 Sender 决定（设计文档 4.8、待核实问题 1）：
- ConsoleSender：把验证码打印到服务端日志。只给 dev / staging 用，prod 启动时会拒绝它。
- AliyunSmsSender：阿里云短信（2026-10-14 用户选定）。只能发手机号，邮箱登录在它下面会被直接拒绝。
新的 Sender 实现 send(contact, code)，能力有限时再实现 accepts(contact)。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import sys
import time
import urllib.parse
import urllib.request
import uuid

from store import Store, now

CODE_TTL = 300          # 验证码 5 分钟有效
RESEND_GAP = 60         # 同一联系方式 60 秒内只发一次
MAX_ATTEMPTS = 5        # 同一个验证码最多试 5 次
TOKEN_TTL = 30 * 86400  # 登录态 30 天

PHONE = re.compile(r"^1[3-9]\d{9}$")
EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class AuthError(Exception):
    pass


class ConsoleSender:
    name = "console"

    def send(self, contact: str, code: str) -> None:
        print(f"[login-code] {contact} -> {code}", file=sys.stderr, flush=True)


def aliyun_signature(params: dict, secret: str, method: str = "GET") -> str:
    """阿里云 RPC 接口签名 v1（HMAC-SHA1）：参数按名字排序、按 RFC3986 编码后拼成待签字符串。
    用官方文档的示例做了测试（tests/test_platform.py SmsSenderTests）。"""
    enc = lambda v: urllib.parse.quote(str(v), safe="~")
    canonical = "&".join(f"{enc(k)}={enc(params[k])}" for k in sorted(params))
    to_sign = f"{method}&{enc('/')}&{enc(canonical)}"
    digest = hmac.new(f"{secret}&".encode(), to_sign.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


class AliyunSmsSender:
    """阿里云短信服务 SendSms（Dysmsapi 2017-05-25）。密钥从环境变量来，不进代码、不进日志。"""
    name = "aliyun"
    ENDPOINT = "https://dysmsapi.aliyuncs.com/"

    def __init__(self, key_id: str, key_secret: str, sign_name: str, template_code: str, timeout: int = 10):
        self.key_id, self.key_secret, self.sign_name, self.template_code, self.timeout = key_id, key_secret, sign_name, template_code, timeout

    def accepts(self, contact: str) -> bool:
        return bool(PHONE.fullmatch(contact))

    def send(self, contact: str, code: str) -> None:
        params = {
            "AccessKeyId": self.key_id, "Action": "SendSms", "Format": "JSON", "PhoneNumbers": contact,
            "RegionId": "cn-hangzhou", "SignName": self.sign_name, "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": uuid.uuid4().hex, "SignatureVersion": "1.0", "TemplateCode": self.template_code,
            "TemplateParam": json.dumps({"code": code}), "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "Version": "2017-05-25",
        }
        params["Signature"] = aliyun_signature(params, self.key_secret)
        url = self.ENDPOINT + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                result = json.load(resp)
        except Exception as exc:  # 网络、HTTP 4xx/5xx：只记类型，不记带签名的 URL
            print(f"[sms] aliyun request failed: {type(exc).__name__}", file=sys.stderr, flush=True)
            raise AuthError("验证码发送失败，请稍后再试") from None
        if result.get("Code") != "OK":
            print(f"[sms] aliyun rejected: {result.get('Code')} {result.get('Message')}", file=sys.stderr, flush=True)
            if result.get("Code") == "isv.BUSINESS_LIMIT_CONTROL":
                raise AuthError("这个手机号今天收到的验证码太多了，请稍后再试")
            raise AuthError("验证码发送失败，请稍后再试")


def normalize(contact: str) -> str:
    contact = (contact or "").strip().lower()
    # 邮箱中的连字符和加号属于真实地址，不能按手机号格式清除。
    if EMAIL.fullmatch(contact):
        return contact
    phone = re.sub(r"\s|-", "", contact)
    if phone.startswith("+86"):
        phone = phone[3:]
    if PHONE.fullmatch(phone):
        return phone
    raise AuthError("请输入正确的手机号或邮箱")


def _hash(code: str, secret: str) -> str:
    return hmac.new(secret.encode(), code.encode(), hashlib.sha256).hexdigest()


class Auth:
    def __init__(self, store: Store, sender, secret: str):
        self.store, self.sender, self.secret = store, sender, secret

    def request_code(self, contact: str) -> dict:
        contact = normalize(contact)
        if hasattr(self.sender, "accepts") and not self.sender.accepts(contact):
            raise AuthError("目前只支持手机号登录")  # 短信发不到邮箱：先拒绝，不生成验证码
        existing = self.store.one("SELECT sent_at FROM login_codes WHERE contact=?", (contact,))
        if existing and now() - existing["sent_at"] < RESEND_GAP:
            raise AuthError("验证码已发送，请稍等一分钟再试")
        code = f"{secrets.randbelow(1_000_000):06d}"
        with self.store.conn() as c:
            c.execute("INSERT INTO login_codes VALUES (?,?,?,?,?) ON CONFLICT(contact) DO UPDATE SET "
                      "code_hash=excluded.code_hash, expires_at=excluded.expires_at, attempts=0, sent_at=excluded.sent_at",
                      (contact, _hash(code, self.secret), now() + CODE_TTL, 0, now()))
        self.sender.send(contact, code)
        is_new = self.store.user_by_contact(contact) is None
        return {"contact": contact, "new_user": is_new, "_code": code}  # _code 只在 dev 环境回给前端

    def verify(self, contact: str, code: str, invite: str | None, consent: bool) -> tuple[dict, str]:
        """验证通过返回 (user, token)。新用户必须带邀请码并勾选同意协议。"""
        contact = normalize(contact)
        row = self.store.one("SELECT * FROM login_codes WHERE contact=?", (contact,))
        if not row or row["expires_at"] < now():
            raise AuthError("验证码已过期，请重新获取")
        if row["attempts"] >= MAX_ATTEMPTS:
            raise AuthError("尝试次数过多，请重新获取验证码")
        if not hmac.compare_digest(row["code_hash"], _hash(str(code).strip(), self.secret)):
            with self.store.conn() as c:
                c.execute("UPDATE login_codes SET attempts = attempts + 1 WHERE contact=?", (contact,))
            raise AuthError("验证码不对")
        user = self.store.user_by_contact(contact)
        if user is None:
            if self.store.flag("signup_open") != "1":
                raise AuthError("内测名额已满，暂不开放注册")
            if not consent:
                raise AuthError("请先阅读并同意用户协议和隐私政策")
            if not invite:
                raise AuthError("首次登录需要邀请码")
            try:
                user = self.store.register(contact, invite)
            except ValueError as exc:
                raise AuthError(str(exc)) from None
        with self.store.conn() as c:
            c.execute("DELETE FROM login_codes WHERE contact=?", (contact,))
        token = secrets.token_urlsafe(32)
        with self.store.conn() as c:
            c.execute("INSERT INTO auth_tokens VALUES (?,?,?)", (token, user["id"], now() + TOKEN_TTL))
        return user, token

    def user_for(self, token: str | None) -> dict | None:
        if not token:
            return None
        row = self.store.one("SELECT user_id FROM auth_tokens WHERE token=? AND expires_at>?", (token, now()))
        return self.store.user(row["user_id"]) if row else None

    def logout(self, token: str) -> None:
        with self.store.conn() as c:
            c.execute("DELETE FROM auth_tokens WHERE token=?", (token,))
