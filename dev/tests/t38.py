import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    cdp = await pg.context.new_cdp_session(pg)
    async def swipe(x1,y1,x2,y2,steps=6):
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':x1,'y':y1}]})
        for i in range(1,steps+1): await cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':[{'x':x1+(x2-x1)*i/steps,'y':y1+(y2-y1)*i/steps}]})
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]}); await pg.wait_for_timeout(450)
    # 1) 휴지통
    n0 = await pg.locator('.grid .chip').count()
    await pg.locator('.cell.today').tap(); await pg.wait_for_selector('.ov.mid'); title = (await pg.locator('.ov.mid .item .tt >> nth=0').inner_text()).strip(); await pg.locator('.ov.mid .item >> nth=0').tap(); await pg.wait_for_selector('.dtitle')
    await pg.locator('.dfoot button:has-text("삭제")').tap(); await pg.wait_for_selector('#cf'); print('삭제 확인 창:', (await pg.locator('#cf').inner_text()).replace('\n',' | ')[:150]); await pg.locator('#cf button:has-text("예")').tap(); await pg.wait_for_timeout(500)
    print('삭제 뒤 달력 칩:', n0, '→', await pg.locator('.grid .chip').count(), '|', title.replace('\n',' '))
    await pg.locator('.tabs button:nth-child(4)').tap(); await pg.wait_for_selector('#trashbox'); print('휴지통:', (await pg.locator('#trashbox').inner_text()).replace('\n',' | ')[:200], '| 제목:', await pg.evaluate("[...document.querySelectorAll('main h2')].map(h=>h.innerText).find(t=>t.startsWith('휴지통'))"))
    await pg.locator('#trashbox').scroll_into_view_if_needed(); await pg.screenshot(path='s50_trash.png')
    await pg.locator('#trashbox button:has-text("복구")').tap(); await pg.wait_for_timeout(500); print('복구 뒤 휴지통 카드 있음:', await pg.locator('#trashbox').count(), '| 안내:', await pg.locator('#toast').inner_text())
    await pg.locator('.tabs button:nth-child(1)').tap(); await pg.wait_for_selector('.grid'); await pg.wait_for_timeout(300); print('복구 뒤 달력 칩:', await pg.locator('.grid .chip').count())
    # 2) 팀 보기 좌우 밀기
    await pg.locator('.tabs button:nth-child(2)').tap(); await pg.wait_for_selector('table.team'); lab = lambda: pg.locator('.nav .label').inner_text(); st = lambda: pg.evaluate("(()=>{const w=document.querySelector('.twrap');return [Math.round(w.scrollLeft), w.scrollWidth-w.clientWidth]})()")
    w0 = await lab(); bb = await pg.locator('.twrap').bounding_box(); y = bb['y'] + 60
    await pg.evaluate("document.querySelector('.twrap').scrollLeft = 0"); print('시작:', w0, await st())
    await swipe(300,y,80,y); print('표 처음 위치에서 왼쪽으로 밀기(표 스크롤이 먼저, 주는 그대로):', await lab()==w0)
    await pg.evaluate("(()=>{const w=document.querySelector('.twrap'); w.scrollLeft = w.scrollWidth})()"); await swipe(300,y,80,y); w1 = await lab(); print('표 오른쪽 끝에서 왼쪽으로 밀기 → 다음 주:', w1, await st())
    await swipe(80,y,300,y); w2 = await lab(); print('표 왼쪽 끝에서 오른쪽으로 밀기 → 이전 주:', w2, await st(), w2==w0)
    my = (await pg.locator('.mode').bounding_box())['y'] + 15
    await swipe(300,my,80,my); print('표 밖(팀원별/거래처별 줄)에서 밀기 → 다음 주:', await lab())
    await pg.locator('.mode button:has-text("거래처별")').tap(); await pg.wait_for_timeout(200); bb = await pg.locator('.twrap').bounding_box(); await pg.evaluate("(()=>{const w=document.querySelector('.twrap'); w.scrollLeft = w.scrollWidth})()"); wa = await lab(); await swipe(300,bb['y']+50,80,bb['y']+50); print('거래처별에서도:', wa, '→', await lab())
    # 3) 거래처 화면
    await pg.locator('button:has-text("오늘")').tap(); await pg.wait_for_timeout(300); await pg.locator('td.who.k >> nth=0').tap(); await pg.wait_for_selector('.kpage'); await pg.screenshot(path='s51_kpage.png')
    print('거래처 화면 글씨:', await pg.evaluate("(()=>{const l=getComputedStyle(document.querySelector('.kpage .dlab')), d=getComputedStyle(document.querySelector('.kpage .item .ss')); return ['제목 '+l.fontSize+' '+l.fontWeight+' '+l.color, '날짜 '+d.fontSize+' '+d.color+' '+d.opacity]})()"), errs)
    await b.close()
asyncio.run(main())
