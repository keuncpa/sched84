import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members .ordpair'); await pg.locator('#members .ord:not([disabled]) >> nth=0').click(); await pg.wait_for_timeout(300)
    await pg.evaluate("""() => { const d = JSON.parse(localStorage.getItem('sched84-demo')); for (let i = 0; i < 43; i++) d.clients.push({ id: 'k' + i, name: '거래처' + (i + 1), color: ['h200','s20','h140','s280','orange','teal'][i % 6], active: i % 5 !== 0 }); localStorage.setItem('sched84-demo', JSON.stringify(d)); }""")
    await pg.reload(); await pg.wait_for_selector('.grid'); await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#kbox')
    n = lambda: pg.locator('#kbox .item').count()
    bb = await pg.locator('#kbox').bounding_box(); print('목록 높이:', round(bb['height']), 'px | 보이는 줄(숨김 제외):', await n(), '| 접힘 버튼:', await pg.locator('button.link:has-text("숨긴 거래처")').inner_text())
    await pg.locator('#kbox').scroll_into_view_if_needed(); await pg.screenshot(path='s47_clients.png')
    await pg.click('button.link:has-text("숨긴 거래처")'); print('숨김 펼침:', await n(), await pg.locator('button.link:has-text("숨긴 거래처")').inner_text())
    await pg.fill('input[aria-label="거래처 검색"]', '거래처1'); print('검색 "거래처1":', await n(), '| 입력 칸 유지:', await pg.evaluate("document.activeElement.getAttribute('aria-label')"))
    await pg.fill('input[aria-label="거래처 검색"]', '없는이름'); print('없는 이름:', await pg.locator('#kbox').inner_text())
    await pg.fill('input[aria-label="거래처 검색"]', 'A사'); await pg.click('#kbox .item >> nth=0'); await pg.wait_for_selector('.sheet input'); print('눌러서 수정 창:', await pg.locator('.sheet input[type=text]').first.input_value())
    await pg.mouse.click(5,5); await pg.wait_for_timeout(200); await pg.click('button:has-text("+ 추가")'); await pg.wait_for_selector('.sheet input'); print('추가 창 열림:', await pg.locator('.sheet h3').inner_text(), errs)
    await b.close()
asyncio.run(main())
