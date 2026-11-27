import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        print('"관리자 배정" 글자 남아있나:', '관리자 배정' in await pg.locator('body').inner_text())
        # 새 일정 + 배정 + 역할
        await pg.click('.fab'); await pg.wait_for_selector('.pick'); await pg.fill('.sheet input[type=text]', 'F사 기말감사')
        print('선택 전 역할 목록:', await pg.locator('.roles').count())
        for n in ['김회계','이감사','박결산']: await pg.click(f'.pick button:has-text("{n}")')
        print('기본 역할(프로필 직급에서 추정):', await pg.evaluate("[...document.querySelectorAll('.roles > div')].map(d => d.querySelector('span').innerText + '=' + (d.querySelector('select').value || '없음'))"))
        await pg.select_option('.roles > div:has-text("이감사") select', label='인차지'); await pg.select_option('.roles > div:has-text("박결산") select', label='스탭')
        await pg.locator('.sheet').screenshot(path='s30_roles_form.png')
        await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(500)
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('tbody .chip:has-text("F사 기말감사") >> nth=0'); await pg.wait_for_selector('.dtitle')
        txt = await pg.locator('.ov.full').inner_text(); print('상세:', txt.replace('\n',' | ')[:230]); print(' 태그 없음:', '관리자 배정' not in txt)
        await pg.screenshot(path='s31_roles_detail.png')
        # 수정: 역할만 변경 + 한 명 해제
        await pg.click('.ov.full button:has-text("수정")'); await pg.wait_for_selector('.roles')
        print('수정 화면 기존 역할:', await pg.evaluate("[...document.querySelectorAll('.roles > div')].map(d => d.querySelector('span').innerText + '=' + (d.querySelector('select').value || '없음'))"))
        await pg.select_option('.roles > div:has-text("김회계") select', value=''); await pg.click('.pick button:has-text("박결산")'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(500)
        await pg.click('tbody .chip:has-text("F사 기말감사") >> nth=0'); await pg.wait_for_selector('.dtitle'); print('변경 후:', (await pg.locator('.dwho').inner_text()).replace('\n',' '))
        await pg.click('.ov.full button:has-text("닫기")')
        # 기존 데모 배정 일정(A사 중간감사)의 역할 순서: 매니저 → 인차지 → 스탭
        await pg.click('tbody .chip:has(b:text-is("A사")) >> nth=0'); await pg.wait_for_selector('.dtitle'); print('A사 역할 순 정렬:', (await pg.locator('.dwho').inner_text()).replace('\n',' '))
        await pg.click('.ov.full button:has-text("닫기")')
        # 개인 일정은 프로필 직급 표시
        await pg.click('tbody tr:has-text("이감사") .chip:has-text("B사") >> nth=0'); await pg.wait_for_selector('.dtitle'); print('개인 일정 담당:', (await pg.locator('.dwho').inner_text()).replace('\n',' '))
        t = await pg.locator('body').inner_text(); print('stray:', [w for w in ['false','null','undefined','NaN'] if w in t], errs)
        await b.close()
asyncio.run(main())
