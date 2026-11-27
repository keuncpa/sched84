import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=3, color_scheme='dark')).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        # 실제와 비슷한 긴 거래처 이름으로 일정 추가
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=거래처 관리')
        for nm, col in [('한주에이알티','s120'),('엘비세미콘','s20')]:
            await pg.click('button:has-text("+ 거래처 추가")'); await pg.wait_for_selector('.sw.many'); await pg.fill('.sheet input[type=text]', nm); await pg.click(f'.sw.many button.c-{col}'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(350)
        await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid')
        for title, cl in [('내부회계','한주에이알티'),('재고실사','엘비세미콘')]:
            await pg.click('.fab'); await pg.wait_for_selector('.sheet form'); await pg.fill('.sheet input[type=text]', title); await pg.select_option('select.inp', label=cl); await pg.click('.pick button:has-text("김회계")'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        chips = await pg.evaluate("[...document.querySelectorAll('.cell .chip')].map(c => [...c.childNodes].map(n => n.nodeType===1 ? n.tagName+':'+n.innerText : 'T:'+n.textContent).join(' | '))")
        for c in sorted(set(chips)): print('  chip:', c)
        await pg.locator('.grid').screenshot(path='s34_cal_chips.png')
        fit = await pg.evaluate("[...document.querySelectorAll('.cell.today .chip b, .cell.today .chip u')].map(x => [x.innerText, x.scrollWidth <= x.clientWidth + 1])"); print('  오늘 칸 글자가 칸 안에 다 들어가나:', fit)
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.locator('.twrap').screenshot(path='s35_team_chips.png')
        print('  팀 보기 칩:', sorted(set(await pg.evaluate("[...document.querySelectorAll('table.team .chip')].map(c => c.innerText.replace(/\\n/g,' / '))")))[:8], errs)
        await b.close()
asyncio.run(main())
