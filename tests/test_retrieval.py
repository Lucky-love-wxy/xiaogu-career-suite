import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/xiaogu_search.py'
def run(kind, query):
    p=subprocess.run([sys.executable,str(SCRIPT),kind,'--query',query],capture_output=True,text=True,check=True)
    return json.loads(p.stdout)
def main():
    r=run('jargon','结果导向与弹性工作'); assert r['status']=='matched' and len(r['matches'])==2
    r=run('occupation','推荐算法工程师负责模型和线上实验'); assert r['matches'][0]['id']=='recommendation-algorithm-engineer'
    r=run('occupation','宠物营养师'); assert r['status']=='index_miss'
    r=run('analyze','数据工程师，快速迭代'); assert r['jargon']['status']=='matched' and r['occupation']['status']=='matched'
    print('retrieval-tests: 4 passed')
if __name__=='__main__': main()
