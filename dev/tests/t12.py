import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        print('filter chips:', await pg.evaluate("[...document.querySelectorAll('.fchip')].map(b=>b.innerText)"))
        await pg.locator('.cell:has(.chip)').first.click(); await pg.wait_for_selector('.ov.mid .item'); await pg.screenshot(path='s18_day_tags.png')
        print('day item:', (await pg.locator('.ov.mid .item >> nth=1').inner_text()).replace('\n',' | '))
        await pg.click('.ov.mid button:has-text("닫기")')
        cats = lambda: pg.evaluate("[...document.querySelectorAll('.card.list .item .tt')].filter(e=>e.querySelector('i.dot')).map(e=>e.innerText.replace(/\\n/g,' '))")
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=일정 유형 관리')
        print('cats:', await cats())
        # 추가
        await pg.click('button:has-text("+ 유형 추가")'); await pg.wait_for_selector('.sw')
        await pg.fill('.sheet input[type=text]', '재고실사'); await pg.click('.sw button.c-orange'); await pg.screenshot(path='s19_cat_form.png')
        await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400); print('after add:', await cats())
        # 순서: 재고실사를 맨 위로 (▲ 4번)
        for _ in range(4):
            await pg.click('.item:has-text("재고실사") button[aria-label="위로"]'); await pg.wait_for_timeout(250)
        print('after move up x4:', await cats())
        # 이름 변경 + 부서공통 체크
        await pg.click('.item:has-text("마감·기한") >> button >> nth=0'); await pg.wait_for_selector('.sw'); await pg.fill('.sheet input[type=text]', '보고서 마감'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        # 사용 중 유형 삭제 → 거부, 숨기기
        await pg.click('.item:has-text("휴가·교육") >> button >> nth=0'); await pg.wait_for_selector('.sw'); await pg.click('.sheet .btn.danger'); await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(300)
        print('delete in-use toast:', await pg.locator('#toast').inner_text())
        await pg.click('.sheet button:has-text("숨기기")'); await pg.wait_for_timeout(400); print('after hide/rename:', await cats())
        await pg.screenshot(path='s20_settings_cats.png', full_page=True)
        # 일정 추가 폼: 새 유형 선택 가능, 숨긴 유형은 없음
        await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid'); await pg.click('.fab'); await pg.wait_for_selector('.seg')
        print('form types:', await pg.evaluate("[...document.querySelectorAll('.seg button')].map(b=>b.innerText + (b.classList.contains('on')?'*':''))"))
        await pg.fill('.sheet input[type=text]', 'G사 재고실사'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        chip = pg.locator('.cell .chip:has-text("G사")').first
        print('new chip class:', await chip.get_attribute('class'), '| filter chips:', await pg.evaluate("[...document.querySelectorAll('.fchip')].map(b=>b.innerText)"))
        # 숨긴 유형(휴가)의 기존 일정은 그대로 보이고 수정 폼에선 그 유형이 유지됨
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list'); await pg.click('.item:has-text("교육")'); await pg.click('.sheet button:has-text("수정")'); await pg.wait_for_selector('.seg')
        print('edit hidden-type event types:', await pg.evaluate("[...document.querySelectorAll('.seg button')].map(b=>b.innerText + (b.classList.contains('on')?'*':''))"))
        t = await pg.locator('#app').inner_text(); print('stray:', 'false' in t or 'null' in t or 'undefined' in t, errs)
        await b.close()
asyncio.run(main())
