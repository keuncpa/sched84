import asyncio
from playwright.async_api import async_playwright
UAS={'ios':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1',
'android':'Mozilla/5.0 (Linux; Android 14; SM-S921N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
'kakao':'Mozilla/5.0 (Linux; Android 14; SM-S921N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 KAKAOTALK 11.0.0'}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for k,ua in UAS.items():
            pg = await (await b.new_context(viewport={'width':390,'height':700}, device_scale_factor=2, user_agent=ua)).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8767/index.html'); await pg.wait_for_selector('.auth', timeout=15000)
            print(k, '|', (await pg.locator('#install').inner_text())[:60].replace('\n',' '), '|', errs)
            if k=='ios': await pg.screenshot(path='s8_ios.png')
            await pg.click('#install .x'); print('  closed ->', await pg.locator('#install').count())
        await b.close()
asyncio.run(main())
