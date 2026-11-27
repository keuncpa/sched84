import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844})).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('.mode button:has-text("거래처별")'); await pg.wait_for_timeout(300)
    rows = lambda: pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => r.cells[0].innerText.trim() + ':' + r.querySelectorAll('.chip').length)")
    print('이번 주 거래처 줄:', await rows(), '| 등록 거래처 수:', await pg.evaluate("document.querySelectorAll('.fsel option').length - 1"))
    await pg.click('button[aria-label="다음"]'); await pg.wait_for_timeout(300); print('다음 주:', await rows())
    for _ in range(6): await pg.click('button[aria-label="다음"]')
    await pg.wait_for_timeout(300); print('한참 뒤 주:', await rows())
    await pg.click('button:has-text("오늘")'); await pg.wait_for_timeout(300)
    opts = await pg.evaluate("[...document.querySelectorAll('.fsel option')].map(o=>[o.value,o.text])"); await pg.select_option('.fsel', opts[1][0]); await pg.wait_for_timeout(300); print('거래처 하나 선택(', opts[1][1], '):', await rows())
    await pg.select_option('.fsel', ''); await pg.wait_for_timeout(200)
    await pg.click('tbody .chip >> nth=0'); await pg.wait_for_selector('.dtitle'); print('상세:', (await pg.locator('.ov.full .sheet').inner_text()).replace('\n',' | ')[:200]); print('errs', errs)
    await b.close()
asyncio.run(main())
