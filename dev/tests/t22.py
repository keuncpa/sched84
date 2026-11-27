import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=3, color_scheme='dark')).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=거래처 관리')
        for nm, col in [('한주에이알티','s120'),('엘비세미콘','s20')]:
            await pg.click('button:has-text("+ 거래처 추가")'); await pg.wait_for_selector('.sw.many'); await pg.fill('.sheet input[type=text]', nm); await pg.click(f'.sw.many button.c-{col}'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(350)
        await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid')
        for title, cl in [('내부회계','한주에이알티'),('재고실사','엘비세미콘')]:
            await pg.click('.fab'); await pg.wait_for_selector('.sheet form'); await pg.fill('.sheet input[type=text]', title); await pg.select_option('select.inp', label=cl); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(3600)
        clipped = await pg.evaluate("[...document.querySelectorAll('.cell')].filter(c => c.scrollHeight > c.clientHeight + 1).map(c => c.querySelector('.num').innerText)")
        print('칩이 칸 밖으로 잘리는 날짜:', clipped or '없음')
        print('오늘 칸:', await pg.evaluate("[...document.querySelectorAll('.cell.today .chip')].map(c => [...c.children].map(x => x.innerText + (x.scrollHeight > x.clientHeight + 1 || x.scrollWidth > x.clientWidth + 1 ? '(잘림)' : '')).join(' / ') || c.innerText)"))
        await pg.evaluate("window.scrollTo(0, 120)"); await pg.wait_for_timeout(200); await pg.screenshot(path='s36_cal_final.png')
        print(errs); await b.close()
asyncio.run(main())
