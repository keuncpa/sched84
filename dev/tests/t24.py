import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, color_scheme='dark')).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('.mode button:has-text("거래처별")'); await pg.wait_for_timeout(200)
        rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText, [...new Set([...r.querySelectorAll('.chip')].map(c => c.innerText))].join(' | ')])")
        for r in rows: print('  ', r)
        await pg.screenshot(path='s38_team_client_titles.png')
        await pg.click('tbody .chip >> nth=0'); await pg.wait_for_selector('.dtitle'); print('칩 누르면 상세(배정 인원):', (await pg.locator('.dwho').inner_text()).replace('\n',' '), errs)
        await b.close()
asyncio.run(main())
