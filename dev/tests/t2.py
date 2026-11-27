import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8766/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=구성원')
        print('self demote btn (should be 0):', await pg.locator('.item:has-text("나(데모)") button').count())
        await pg.click('.item:has-text("김회계") button:has-text("관리자 지정")'); await pg.wait_for_timeout(300)
        print('김회계 badge:', await pg.locator('.item:has-text("김회계") .badge').inner_text())
        print('self demote btn now:', await pg.locator('.item:has-text("나(데모)") button').inner_text())
        await pg.click('.item:has-text("나(데모)") button'); await pg.wait_for_timeout(300)
        print('admin buttons visible after self-demote:', await pg.locator('.item button').count())
        await pg.screenshot(path='s7.png'); print(errs); await b.close()
asyncio.run(main())
