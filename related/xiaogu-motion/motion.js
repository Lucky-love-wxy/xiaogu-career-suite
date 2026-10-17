(() => {
  'use strict';
  const stage = document.querySelector('#stage');
  const character = document.querySelector('#character');
  const speech = document.querySelector('#speech');
  const pause = document.querySelector('#pause');
  const speedButton = document.querySelector('#speed');
  const themeButton = document.querySelector('#theme');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const modes = {
    idle: ['自在待机', '嗨，今天想一起做点什么？'],
    happy: ['开心一下', '见到你，今天又多了一点开心。'],
    think: ['认真思考', '让我想想……也许还有另一种可能。'],
    focus: ['进入专注', '你负责灵感，我陪你把它变成现实。'],
    cheer: ['为你加油', '慢慢来，你已经在向前走了！']
  };
  let speed = 1;
  let greetingTimer;
  let greetingOrigin;
  function setMode(mode) {
    if (!modes[mode]) return;
    clearTimeout(greetingTimer);
    greetingOrigin = undefined;
    stage.dataset.mood = mode;
    document.querySelector('#mood-label').textContent = modes[mode][0];
    speech.textContent = modes[mode][1];
    document.querySelectorAll('[data-mode]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
    });
  }
  function greet() {
    const previous = greetingOrigin || stage.dataset.mood;
    setMode('cheer');
    greetingOrigin = previous;
    speech.textContent = '你好呀！很高兴和你一起。';
    greetingTimer = setTimeout(() => setMode(previous), 3800);
  }
  document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setMode(button.dataset.mode)));
  document.querySelector('#greet').addEventListener('click', greet);
  character.addEventListener('click', greet);
  character.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); greet(); }
  });
  document.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch' || document.body.classList.contains('paused') || reduced.matches) return;
    const rect = character.getBoundingClientRect();
    const x = Math.max(-7, Math.min(7, (event.clientX - rect.left - rect.width / 2) / 35));
    const y = Math.max(-4, Math.min(4, (event.clientY - rect.top - rect.height * .46) / 45));
    stage.style.setProperty('--look-x', `${x}px`);
    stage.style.setProperty('--look-y', `${y}px`);
  });
  document.addEventListener('pointerleave', () => {
    stage.style.setProperty('--look-x', '0px'); stage.style.setProperty('--look-y', '0px');
  });
  pause.addEventListener('click', () => {
    const paused = document.body.classList.toggle('paused');
    pause.textContent = paused ? '播放' : '暂停';
    pause.setAttribute('aria-pressed', String(paused));
    pause.setAttribute('aria-label', paused ? '播放动效' : '暂停动效');
  });
  speedButton.addEventListener('click', () => {
    speed = speed === 1 ? .5 : speed === .5 ? 1.5 : 1;
    speedButton.textContent = `${speed}×`;
    stage.style.setProperty('--duration', `${4 / speed}s`);
    stage.style.setProperty('--blink', `${6 / speed}s`);
    stage.style.setProperty('--quick', `${1.2 / speed}s`);
  });
  themeButton.addEventListener('click', () => {
    const night = document.body.classList.toggle('night');
    themeButton.innerHTML = `${night ? '日间场景' : '夜间场景'} <span aria-hidden="true">↗</span>`;
    themeButton.setAttribute('aria-pressed', String(night));
    themeButton.setAttribute('aria-label', night ? '切换日间场景' : '切换夜间场景');
  });
  const applyReduced = () => {
    document.body.classList.toggle('reduced', reduced.matches);
    pause.disabled = reduced.matches;
    speedButton.disabled = reduced.matches;
    pause.textContent = reduced.matches ? '静态' : document.body.classList.contains('paused') ? '播放' : '暂停';
    pause.setAttribute('aria-label', reduced.matches ? '已按系统偏好减少动态' : document.body.classList.contains('paused') ? '播放动效' : '暂停动效');
  };
  reduced.addEventListener('change', applyReduced);
  applyReduced();
})();
