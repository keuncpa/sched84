import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    # 거래처 있는 날 찾아 열기
    cells = pg.locator('.cell:not(.out)'); n = await cells.count(); hit=None
    for i in range(n):
        if await cells.nth(i).locator('.chip b').count(): hit=i; break
    await cells.nth(hit).click(); await pg.wait_for_selector('.dnav')
    get = lambda: pg.evaluate("({h:document.querySelector('.dnav h3').innerText, items:[...document.querySelectorAll('.ov .item .tt')].map(x=>{const b=x.querySelector('.badge');return (b?'['+b.innerText+'] ':'')+'<'+[...x.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('')+'>'}), sel:document.querySelector('.cell.sel')?.innerText.split('\\n')[0], mon:document.querySelector('header')?.innerText.split('\\n')[0]})")
    print('연 날:', await get()); await pg.screenshot(path='s54_day.png')
    for i in range(3): await pg.click('button[aria-label="다음 날"]'); await pg.wait_for_timeout(150)
    print('다음 날 x3:', await get())
    for i in range(40): await pg.click('button[aria-label="전날"]'); await pg.wait_for_timeout(40)
    await pg.wait_for_timeout(500); print('전날 x40:', await get()); await pg.screenshot(path='s55_day_prev.png')
    await pg.click('.ov .btn.ghost'); print('닫힌 뒤 달:', await pg.evaluate("document.querySelector('.cell.sel')?.innerText.split('\\n')[0]"))
    # 거래처만 고르고 제목 없이 저장
    await pg.click('.fab'); await pg.wait_for_selector('.sheet form'); print('라벨(거래처 전):', await pg.evaluate("[...document.querySelectorAll('.sheet form > label')].map(l=>l.innerText)"))
    await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(300); print('제목없이·거래처없이:', await pg.evaluate("document.querySelector('.toast')?.innerText"), '폼 열림', await pg.locator('.sheet form').count())
    opt = await pg.evaluate("document.querySelector('.sheet select.inp').options[1].text"); await pg.select_option('.sheet select.inp', index=1)
    print('라벨(거래처 후):', await pg.evaluate("[...document.querySelectorAll('.sheet form > label')].map(l=>l.innerText)"))
    await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(600)
    ev = await pg.evaluate("JSON.parse(localStorage.getItem('sched84-demo')).events.filter(e=>e.title==='')"); print('빈 제목 저장:', len(ev), opt)
    await pg.wait_for_selector('.cell.sel'); await pg.click('.cell.sel'); await pg.wait_for_selector('.dnav'); print('그날 목록:', (await get())['items'])
    await pg.locator('.ov .item').filter(has_text=opt).last.click(); await pg.wait_for_selector('.dtitle'); print('상세 제목:', repr(await pg.locator('.dtitle').inner_text())); await pg.screenshot(path='s56_detail_blank.png')
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.screenshot(path='s57_team.png')
    # 팀 보기 거래처별 → 칩 → 날 창 → 주 넘어가기
    print('오류:', errs); await b.close()
asyncio.run(main())
