import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1)).new_page()
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); await pg.wait_for_timeout(400); await pg.screenshot(path='e1.png')
    await pg.click('.ov.mid .item >> nth=0'); await pg.wait_for_selector('.dtitle'); await pg.wait_for_timeout(600); await pg.screenshot(path='e2.png')
    print(await pg.evaluate("[getComputedStyle(document.querySelector('.dtitle')).color, getComputedStyle(document.querySelector('.dtitle')).opacity, document.querySelector('.dbody').className, getComputedStyle(document.querySelector('.dbody')).opacity]"))
    await pg.click('.dtop button'); await pg.mouse.click(5,5); await pg.wait_for_timeout(200)
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.screenshot(path='e3.png')
    await b.close()
asyncio.run(main())
