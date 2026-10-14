(async () => {
  const checks = [];
  const check = (name, passed, detail = '') => checks.push({name, passed:!!passed, detail});
  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  const stage = document.querySelector('#stage');
  const $ = selector => document.querySelector(selector);
  const transform = () => getComputedStyle($('.body-float')).transform;
  check('page loaded', document.title.includes('小谷') && !!stage);
  check('desktop has no horizontal overflow', document.documentElement.scrollWidth === innerWidth);
  const before = transform(); await wait(240);
  check('idle animation advances', before !== transform());
  for (const mode of ['happy','think','focus','cheer','idle']) {
    $(`[data-mode="${mode}"]`).click();
    check(`mode ${mode}`, stage.dataset.mood === mode && $(`[data-mode="${mode}"]`).getAttribute('aria-pressed') === 'true');
  }
  $('[data-mode="focus"]').click(); await wait(1000);
  check('focus laptop visible', Number(getComputedStyle($('.laptop')).opacity) > .95, getComputedStyle($('.laptop')).opacity);
  $('#pause').click(); await wait(60); const frozen = transform(); await wait(200);
  check('pause freezes animation', frozen === transform() && $('#pause').textContent === '播放');
  $('#pause').click();
  check('resume control', !document.body.classList.contains('paused'));
  $('#speed').click(); check('half speed', $('#speed').textContent === '0.5×' && getComputedStyle($('.body-float')).animationDuration === '8s');
  $('#speed').click(); check('fast speed', $('#speed').textContent === '1.5×'); $('#speed').click();
  $('#theme').click(); check('night scene', document.body.classList.contains('night') && $('#theme').getAttribute('aria-pressed') === 'true'); $('#theme').click();
  document.dispatchEvent(new PointerEvent('pointermove', {clientX:innerWidth,clientY:innerHeight,pointerType:'mouse'}));
  check('gaze responds', stage.style.getPropertyValue('--look-x') === '7px');
  document.dispatchEvent(new PointerEvent('pointerleave'));
  $('#character').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
  check('keyboard greeting', stage.dataset.mood === 'cheer' && $('#speech').textContent.includes('你好'));
  await wait(200); $('#greet').click(); await wait(3950);
  check('repeated greeting restores original mode',stage.dataset.mood === 'focus');
  $('#greet').click(); $('[data-mode="think"]').click(); await wait(3900);
  check('manual selection cancels greeting restore',stage.dataset.mood === 'think');
  $('[data-mode="idle"]').click();
  check('no observed runtime errors', !(window.__errors || []).length, window.__errors || []);
  return JSON.stringify({viewport:[innerWidth,innerHeight],checks,result:checks.every(item=>item.passed)?'PASS':'FAIL'});
})()
