import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        txt = await pg.locator('#app').inner_text(); print('stray false/null:', 'false' in txt or 'null' in txt)
        # 팀 보기: 배정 일정(A사 중간감사: 나, 김회계, 박결산)이 세 사람 줄에 모두 보이는지
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team')
        rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText.split('\\n')[0], [...new Set([...r.querySelectorAll('.chip')].map(c => c.innerText))].join('|')])")
        for r in rows: print('  ', r)
        # 관리자(데모의 나): 새 일정 + 팀원 배정
        await pg.click('.fab'); await pg.wait_for_selector('.pick')
        await pg.fill('.sheet input[type=text]', 'F사 기말감사')
        await pg.click('.pick button:has-text("이감사")'); await pg.click('.pick button:has-text("김회계")')
        await pg.screenshot(path='s11_assign_form.png')
        await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(500)
        rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText.split('\\n')[0], [...r.querySelectorAll('.chip')].some(c => c.innerText==='F사 기말감사')])")
        print('F사 배정 후 줄별 표시:', rows)
        await pg.screenshot(path='s12_team.png')
        # 상세: 참여/배정 표시, 수정으로 한 명 빼기
        await pg.click('tbody tr .chip:has-text("F사 기말감사") >> nth=0'); await pg.wait_for_selector('.sheet')
        print('detail:', (await pg.locator('.sheet').inner_text()).replace('\n',' | ')[:130])
        await pg.screenshot(path='s13_detail.png')
        await pg.click('.sheet button:has-text("수정")'); await pg.wait_for_selector('.pick')
        print('pre-selected:', await pg.evaluate("[...document.querySelectorAll('.pick button.on')].map(b=>b.innerText)"))
        await pg.click('.pick button:has-text("김회계")'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(500)
        rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText.split('\\n')[0], [...r.querySelectorAll('.chip')].some(c => c.innerText==='F사 기말감사')])")
        print('김회계 해제 후:', rows)
        # 내 일정: 배정받은 A사는 보이고, 내가 배정만 한 E사·F사는 안 보임
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list')
        mine = await pg.evaluate("[...document.querySelectorAll('.item')].map(i => i.innerText.replace(/\\n/g,' / '))")
        for m in mine: print('  mine:', m)
        # 달력 + 내 일정만 필터
        await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid'); await pg.screenshot(path='s14_cal.png')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_timeout(300)
        t = await pg.locator('main').inner_text(); print('settings stray:', 'false' in t or 'null' in t, '| 알림카드(데모에선 숨김):', '배정 알림' in t)
        print('errs', errs); await b.close()
asyncio.run(main())
