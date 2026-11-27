import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':700})).new_page()
        await pg.goto('http://localhost:8768/index.html'); await pg.wait_for_selector('.auth')
        await pg.click('#install .x')
        print('auth text:', repr((await pg.locator('#app').inner_text())[:40]))
        # simulate shell render in live mode without network: stub store via demo? check no stray 'false'/'null'
        await pg.reload(); await pg.wait_for_selector('.auth')
        print('after dismiss reload:', repr((await pg.locator('#app').inner_text())[:30]))
        await b.close()
asyncio.run(main())
