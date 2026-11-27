import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for scheme in ('light','dark'):
            pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, color_scheme=scheme)).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
            print(scheme, 'today cells:', await pg.locator('.cell.today').count(), '| tag:', await pg.locator('.todaytag').inner_text(), errs)
            await pg.locator('.grid').screenshot(path=f's17_today_{scheme}.png')
        await b.close()
asyncio.run(main())
