import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, has_touch=True, is_mobile=True)).new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    cdp = await pg.context.new_cdp_session(pg)
    async def swipe(x1,y1,x2,y2,steps=6):
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':x1,'y':y1}]})
        for i in range(1,steps+1): await cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':[{'x':x1+(x2-x1)*i/steps,'y':y1+(y2-y1)*i/steps}]})
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]}); await pg.wait_for_timeout(350)
    lab = lambda: pg.locator('.nav .label').first.inner_text()
    print('시작:', await lab())
    await swipe(300,400,80,410); print('왼쪽으로 밀기 →', await lab())
    await swipe(80,400,300,395); await swipe(80,400,300,395); print('오른쪽으로 두 번 →', await lab())
    await swipe(200,300,210,600); print('세로로 밀기(변화 없어야) →', await lab())
    await swipe(200,400,170,405); print('살짝만 밀기(변화 없어야) →', await lab())
    fy = (await pg.locator('.filters').bounding_box())['y']+10
    await swipe(300,fy,80,fy); print('유형 줄에서 밀기(변화 없어야) →', await lab())
    await pg.locator('.cell.today, .cell >> nth=10').first.tap(); await pg.wait_for_selector('.ov'); await swipe(300,420,80,420); print('팝업 열린 상태(변화 없어야) →', await lab(), '| 팝업 유지:', await pg.locator('.ov').count()==1)
    await pg.mouse.click(5,5); await pg.wait_for_timeout(300)
    await pg.click('button[aria-label="다음"]'); await pg.wait_for_timeout(200); print('› 버튼 →', await lab())
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); w=await lab(); await swipe(300,400,80,400); print('팀 보기에서 밀기(표 가로 스크롤 유지, 변화 없어야):', w == await lab())
    await pg.click('button[aria-label="다음"]'); await pg.wait_for_timeout(200); print('팀 보기 › 버튼:', w, '→', await lab())
    print('errs', errs); await b.close()
asyncio.run(main())
