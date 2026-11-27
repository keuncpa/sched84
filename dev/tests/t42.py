import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    f = lambda: pg.evaluate("[...document.querySelector('.filters').children].map(x=>x.tagName+':'+(x.options?x.options[0].text:x.innerText))")
    print('달력 필터:', await f()); n0 = await pg.locator('.grid .chip').count()
    await pg.click('.fchip'); print('내 일정만:', n0, '→', await pg.locator('.grid .chip').count()); await pg.click('.fchip')
    await pg.screenshot(path='s58_filters.png', clip={'x':0,'y':0,'width':390,'height':260})
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); print('팀 필터:', await f() if await pg.locator('.filters').count() else '없음')
    print('오류:', errs); await b.close()
asyncio.run(main())
