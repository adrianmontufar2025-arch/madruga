const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage();
  await p.emulateMedia({ media: 'print', colorScheme: 'light' });
  await p.goto('file://' + process.cwd() + '/planos-print.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const fonts = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
  console.log('fonts', [...new Set(fonts)].join(', '));
  const over = await p.evaluate(() => [...document.querySelectorAll('.lat, .texto, .area')].filter(e => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1).map(e => e.className + ' ' + (e.closest('.pg') ? [...document.querySelectorAll('.pg')].indexOf(e.closest('.pg')) + 1 : '') + ' ' + e.scrollHeight + '/' + e.clientHeight + ' ' + e.scrollWidth + '/' + e.clientWidth));
  console.log('overflow', over);
  await p.pdf({ path: 'Casa-Elevada-200msnm-planos.pdf', preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
