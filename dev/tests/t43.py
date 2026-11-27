import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for W in (390, 1280):
        pg = await (await b.new_context(viewport={'width':W,'height':844}, device_scale_factor=2)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members .ordpair'); await pg.locator('#members .ord:not([disabled]) >> nth=0').click(); await pg.wait_for_timeout(300)
        await pg.evaluate("(() => { const d = JSON.parse(localStorage.getItem('sched84-demo')); const names = ['SK하이닉스시스템아이씨','한국핀테크지원센터','E1컨테이너터미널','LB세미콘','동방']; d.clients.slice(0,5).forEach((c,i)=>c.name=names[i]); localStorage.setItem('sched84-demo', JSON.stringify(d)); })()")
        await pg.reload(); await pg.wait_for_selector('.grid'); await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team')
        await pg.click('.mode button:has-text("거래처별")'); await pg.wait_for_timeout(300)
        print(W, await pg.evaluate("[...document.querySelectorAll('td.who.k')].map(x=>x.innerText+' h'+Math.round(x.getBoundingClientRect().height)+' w'+x.clientWidth+'/'+x.scrollWidth)"), '표', await pg.evaluate("[document.querySelector('table.team').offsetWidth, document.querySelector('.twrap').clientWidth, document.querySelector('.team th:nth-child(3)').offsetWidth]"), errs)
        await pg.screenshot(path=f's59_team_k_{W}.png')
        await pg.click('.mode button:has-text("팀원별")'); await pg.wait_for_timeout(200); print('  팀원별 첫 칸', await pg.evaluate("document.querySelector('td.who').offsetWidth"))
    await b.close()
asyncio.run(main())
