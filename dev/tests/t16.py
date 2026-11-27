import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        print('filters:', await pg.evaluate("[document.querySelector('.fsel') ? [...document.querySelector('.fsel').options].map(o=>o.text).join('/') : null, ...[...document.querySelectorAll('.fchip')].map(b=>b.innerText)]"))
        n_all = await pg.locator('.cell .chip').count()
        # 거래처 필터
        await pg.select_option('.fsel', label='A사'); await pg.wait_for_timeout(200)
        print('A사 필터 → chips', n_all, '->', await pg.locator('.cell .chip').count(), await pg.evaluate("[...new Set([...document.querySelectorAll('.cell .chip')].map(c=>c.innerText))]"))
        await pg.select_option('.fsel', value=''); 
        # 색 기준: 거래처
        c0 = await pg.locator('.cell .chip').first.get_attribute('class')
        await pg.click('.fchip:has-text("색: 거래처")'); await pg.wait_for_timeout(200)
        print('색 전환:', c0, '→', await pg.locator('.cell .chip').first.get_attribute('class'), '| 버튼:', await pg.locator('.fchip >> nth=0').inner_text())
        await pg.screenshot(path='s24_cal_client_color.png')
        # 팀 보기 → 거래처별
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('.mode button:has-text("거래처별")'); await pg.wait_for_timeout(200)
        rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText, [...new Set([...r.querySelectorAll('.chip')].map(c => c.innerText))].join(' | ')])")
        for r in rows: print('  ', r)
        await pg.screenshot(path='s25_team_by_client.png')
        # 거래처 상세
        await pg.click('td.who.k:has-text("A사")'); await pg.wait_for_selector('.ov.full')
        print('거래처 상세:', (await pg.locator('.ov.full').inner_text()).replace('\n',' | ')[:330])
        await pg.screenshot(path='s26_client_detail.png')
        await pg.click('.ov.full .item >> nth=0'); await pg.wait_for_selector('.dtitle'); print(' → 일정 상세:', await pg.locator('.dtitle').inner_text(), '| 거래처 버튼:', await pg.locator('button.person').inner_text())
        await pg.click('.ov.full button:has-text("목록으로")'); await pg.wait_for_selector('text=예정·진행 중'); print(' ← 거래처 상세로 복귀 OK')
        await pg.click('.ov.full button:has-text("이 거래처 일정 추가")'); await pg.wait_for_selector('.sheet form')
        print(' 폼 거래처 기본값:', await pg.evaluate("document.querySelector('select.inp').selectedOptions[0].text"))
        await pg.fill('.sheet input[type=text]', 'A사 기말감사'); await pg.click('.pick button:has-text("이감사")'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        # 설정: 거래처 추가·중복·숨김·삭제거부
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=거래처 관리')
        await pg.click('button:has-text("+ 거래처 추가")'); await pg.fill('.sheet input[type=text]', 'a사'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(300); print('중복 이름:', await pg.locator('#toast').inner_text())
        await pg.fill('.sheet input[type=text]', '가나상사'); await pg.click('.sw.many button.c-s320'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        await pg.click('.item:has-text("A사")'); await pg.click('.sheet .btn.danger'); await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(300); print('사용 중 삭제:', await pg.locator('#toast').inner_text())
        await pg.click('.sheet button:has-text("숨기기")'); await pg.wait_for_timeout(400)
        print('거래처 목록:', await pg.evaluate("[...document.querySelectorAll('.card.list .item .tt')].filter(e=>e.querySelector('i.dot') && !e.closest('.item').querySelector('.ord')).map(e=>e.innerText.replace(/\\n/g,' '))"))
        # 퇴사 처리
        mem = lambda: pg.evaluate("[...document.querySelectorAll('h2')].filter(h=>/구성원|퇴사자/.test(h.innerText)).map(h=>h.innerText + ': ' + [...h.nextElementSibling.querySelectorAll('.item .tt')].map(t=>t.innerText.replace(/\\n/g,' ')).join(', '))")
        print(await mem())
        await pg.click('.item:has-text("박결산") button:has-text("퇴사 처리")'); await pg.wait_for_selector('#cf'); print('확인창:', (await pg.locator('#cf').inner_text()).replace('\n',' | ')[:120])
        await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(400); print(await mem()); await pg.screenshot(path='s27_settings_left.png', full_page=True)
        # 퇴사자의 일정은 유지: 팀 보기(팀원별)에 퇴사 표시로 남고, 배정 일정 상세에도 남음
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('.mode button:has-text("팀원별")'); await pg.wait_for_timeout(200)
        rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText.replace(/\\n/g,' '), r.querySelectorAll('.chip').length])"); print('팀원별:', rows)
        await pg.click('tbody tr:has-text("박결산") .chip >> nth=0'); await pg.wait_for_selector('.dtitle'); print('퇴사자 일정 상세:', (await pg.locator('.dwho').inner_text()).replace('\n',' '))
        await pg.click('.ov.full button:has-text("닫기")')
        # 새 일정 배정 목록에는 퇴사자 없음
        await pg.click('.fab'); await pg.wait_for_selector('.pick'); print('배정 후보:', await pg.evaluate("[...document.querySelectorAll('.pick button')].map(b=>b.innerText)")); await pg.click('.sheet button:has-text("취소")')
        # 복귀
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=퇴사자'); await pg.click('.item:has-text("박결산") button:has-text("복귀")'); await pg.wait_for_timeout(400); print(await mem())
        t = await pg.locator('#app').inner_text(); print('stray:', 'false' in t or 'null' in t or 'undefined' in t, errs)
        await b.close()
asyncio.run(main())
