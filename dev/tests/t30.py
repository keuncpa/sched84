import asyncio, openpyxl
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, accept_downloads=True)).new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    order = lambda: pg.evaluate("[...document.querySelectorAll('#members .item')].filter(x=>x.querySelector('.ordpair')).map(x=>x.querySelector('.tt').firstChild.textContent)")
    team = lambda: pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => r.cells[0].innerText.split('\\n')[0] + (r.classList.contains('me') ? '*' : ''))")
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members .ordpair'); print('처음 순서(이름순):', await order())
    await pg.click('button[aria-label="이감사 위로"]'); await pg.wait_for_timeout(300); await pg.click('button[aria-label="이감사 위로"]'); await pg.wait_for_timeout(300)
    await pg.click('button[aria-label="나(데모) 아래로"]'); await pg.wait_for_timeout(300); print('옮긴 뒤:', await order())
    print('맨 위 ▲ 비활성:', await pg.locator('#members .ordpair >> nth=0').locator('.ord >> nth=0').is_disabled(), '| 순서 카드 없음:', await pg.locator('#ordcard').count()==0, '| 구성원 목록:', await pg.evaluate("[...document.querySelectorAll('main h2')].find(h=>h.innerText.startsWith('구성원 (')).nextElementSibling.innerText.replace(/\\n/g,' ').slice(0,90)"))
    await pg.screenshot(path='s41_order.png', full_page=False)
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); print('팀 보기(*=본인 강조):', await team())
    print(' 본인 줄 이름 색:', await pg.evaluate("getComputedStyle(document.querySelector('tr.me .who')).color"), '/ 다른 줄:', await pg.evaluate("getComputedStyle(document.querySelector('tbody tr:not(.me) .who')).color"))
    await pg.screenshot(path='s42_team_me.png')
    await pg.click('.fab'); await pg.wait_for_selector('.pick'); print('배정 목록:', await pg.evaluate("[...document.querySelectorAll('.pick button')].map(b=>b.innerText)")); await pg.mouse.click(5,5); await pg.wait_for_timeout(200)
    await pg.reload(); await pg.wait_for_selector('.grid'); await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#xlbtn'); print('새로 열어도 유지:', await order())
    async with pg.expect_download() as d: await pg.click('#xlbtn')
    await (await d.value).save_as('xl/order.xlsx'); ws=openpyxl.load_workbook('xl/order.xlsx').active
    print('엑셀 사람 줄:', [ws.cell(r,2).value for r in range(11,16) if ws.cell(r,2).value]); print('errs', errs)
    await b.close()
asyncio.run(main())
