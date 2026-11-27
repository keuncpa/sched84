import asyncio, datetime, openpyxl
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, accept_downloads=True)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    today = datetime.date.fromisoformat(await pg.evaluate("(()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')})()"))
    mon = today + datetime.timedelta(days=(7 - today.weekday()))          # 다음 주 월요일
    d = lambda n: (mon + datetime.timedelta(days=n)).isoformat()
    # 다음 주 월~금 일정, 팀원 3명. 그중 '이감사'만 월~수
    await pg.click('.fab'); await pg.wait_for_selector('.sheet form')
    await pg.fill('.sheet input[type=text]', '기간다른일정'); ds = pg.locator('.sheet form > input[type=date], .sheet form .row2 input[type=date]')
    await pg.locator('.sheet input[type=date]').nth(0).fill(d(0)); await pg.locator('.sheet input[type=date]').nth(1).fill(d(4))
    for n in ('나(데모)','김회계','이감사'): await pg.click(f'.pick button:has-text("{n}")')
    print('폼 줄:', await pg.evaluate("[...document.querySelectorAll('.roles .rrow')].map(r=>r.innerText.replace(/\\n/g,' ').slice(0,40))"))
    await pg.click('button[aria-label="이감사 투입 기간"]'); await pg.wait_for_selector('input[aria-label="이감사 종료일"]')
    await pg.fill('input[aria-label="이감사 종료일"]', d(2)); await pg.locator('input[aria-label="이감사 종료일"]').dispatch_event('change')
    await pg.locator('.sheet').screenshot(path='s52_form_span.png')
    await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(600)
    ev = await pg.evaluate("JSON.parse(localStorage.getItem('sched84-demo')).events.find(e=>e.title==='기간다른일정')"); print('저장된 값:', ev['start_date'], ev['end_date'], '사람별:', {k[:2]:v for k,v in ev.get('spans',{}).items()}, '인원', len(ev['members']))
    # 팀 보기 다음 주
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('button[aria-label="다음"]'); await pg.wait_for_timeout(400)
    rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => r.cells[0].innerText.split('\\n')[0] + ': ' + [...r.cells].slice(1).map(c => [...c.querySelectorAll('.chip')].some(x => x.innerText.includes('기간다른')) ? 'O' : '.').join(''))")
    print('팀 보기(월~일):', [r for r in rows if 'O' in r])
    await pg.click('tbody .chip:has-text("기간다른") >> nth=0'); await pg.wait_for_selector('.dtitle'); print('상세:', (await pg.locator('.ov.full .dwho').inner_text()).replace('\n',' | '), '| 기간:', await pg.evaluate("[...document.querySelectorAll('.ov.full .dsec')].map(x=>x.innerText.replace(/\\n/g,' ')).find(t=>t.startsWith('기간'))"))
    await pg.screenshot(path='s53_detail_span.png')
    # 수정 창: 기존 기간이 유지돼 보이는지, 전체 기간으로 되돌리기
    await pg.click('.dfoot button:has-text("수정")'); await pg.wait_for_selector('.sheet form'); print('수정 창:', await pg.evaluate("[...document.querySelectorAll('.roles .rrow')].map(r=>r.querySelector('.r1 span').innerText + ':' + (r.querySelector('.r2') ? [...r.querySelectorAll('.r2 input')].map(i=>i.value.slice(5)).join('~') : '전체'))"))
    await pg.click('.sheet button:has-text("취소")') if await pg.locator('.sheet button:has-text("취소")').count() else await pg.mouse.click(5,5)
    await pg.wait_for_timeout(200)
    # 달력: 목요일(이감사 빠진 날) 목록의 이름
    await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid')
    for _ in range(2):
        if await pg.evaluate("s => !!document.querySelector('.grid')", '') and not await pg.locator('.cell:not(.out)').filter(has_text=str(int(d(3)[8:]))).count(): break
    # 엑셀
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#xlbtn')
    y, m = int(d(0)[:4]), int(d(0)[5:7]); q = (m-1)//3+1; await pg.select_option('select[aria-label="내려받을 기간"]', f'{y}-{q}')
    async with pg.expect_download() as dl: await pg.click('#xlbtn')
    await (await dl.value).save_as('xl/span.xlsx'); ws = openpyxl.load_workbook('xl/span.xlsx').active
    out = []
    for r in range(1, ws.max_row+1):
        for c in range(3, 34):
            v = ws.cell(r,c).value
            if isinstance(v,str) and '기간다른' in v:
                mr = next((x for x in ws.merged_cells.ranges if (r,c) in [(x.min_row,x.min_col)]), None); out.append((ws.cell(r,2).value or '(거래처/위 줄)', f'{mr.max_col-mr.min_col+1 if mr else 1}칸'))
    print('엑셀 줄별 칸 수:', out); print('errs', errs)
    await b.close()
asyncio.run(main())
