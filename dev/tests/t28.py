import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for scheme in ('light','dark'):
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, color_scheme=scheme)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'd_{scheme}_1cal.png')
        if scheme=='light':
            await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); await pg.screenshot(path='d_light_2day.png'); await pg.click('.ov.mid .item >> nth=0'); await pg.wait_for_selector('.dtitle'); await pg.screenshot(path='d_light_3detail.png'); await pg.click('.dtop button'); await pg.mouse.click(5,5); await pg.wait_for_timeout(200)
            await pg.click('.fab'); await pg.wait_for_selector('.sheet form'); await pg.screenshot(path='d_light_4form.png'); await pg.click('.sheet button:has-text("취소")') if await pg.locator('.sheet button:has-text("취소")').count() else await pg.mouse.click(5,5)
            await pg.wait_for_timeout(200)
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.screenshot(path=f'd_{scheme}_5team.png')
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_timeout(300); await pg.screenshot(path=f'd_{scheme}_6mine.png')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_timeout(300); await pg.screenshot(path=f'd_{scheme}_7set.png')
        print(scheme, errs)
    pg = await (await b.new_context(viewport={'width':1280,'height':860})).new_page(); await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid'); await pg.screenshot(path='d_pc.png')
    await b.close()
asyncio.run(main())
