// Runs copied into _work/scripts/ (cdp.js is its flat sibling there — see WORKFLOW §8 scaffold).
const { connect, page: findPage } = require('./cdp');
(async () => {
  const out = process.argv[2] || 'cover/_shots/shot.png';
  const b = await connect();
  const page = await findPage(b, 'chatgpt.com', { fallbackFirst: true });
  await page.bringToFront().catch(()=>{});
  await page.screenshot({ path: out }).catch(async e => { await page.screenshot({ path: out, timeout: 5000 }); });
  console.log('shot ->', out, '| url:', page.url(), '| title:', await page.title());
  await b.close(); // detaches CDP, does not close chrome
})();
