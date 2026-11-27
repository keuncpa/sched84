import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        # 일정이 있는 날(이번 주 월요일 = 데모 A사 중간감사 + 부서 회의) 누르기
        cell = pg.locator('.cell:has(.chip)').first
        await cell.click(); await pg.wait_for_selector('.ov.mid .sheet')
        box = await pg.locator('.ov.mid .sheet').bounding_box(); cy = box['y'] + box['height']/2
        print('popup title:', await pg.locator('.ov.mid h3').inner_text(), '| items:', await pg.locator('.ov.mid .item').count(), '| 세로 중앙 위치: %.0f / 화면 844 (중앙 422)' % cy)
        await pg.screenshot(path='s16_day_popup.png')
        await pg.click('.ov.mid .item >> nth=0'); await pg.wait_for_selector('.ov.full')
        print('detail buttons:', await pg.evaluate("[...document.querySelectorAll('.sheet .btns button')].map(b=>b.innerText)"))
        await pg.click('.sheet button:has-text("목록으로")'); await pg.wait_for_selector('.ov.mid .item'); print('back to day list OK')
        await pg.click('.ov.mid button:has-text("일정 추가")'); await pg.wait_for_selector('.sheet form')
        print('add form start date:', await pg.input_value('.sheet input[type=date] >> nth=0'))
        await pg.click('.sheet button:has-text("취소")')
        # 빈 날짜
        empty = pg.locator('.cell:not(:has(.chip))').first; await empty.click(); await pg.wait_for_selector('.ov.mid .empty'); print('empty day popup OK')
        await pg.mouse.click(5, 5); await pg.wait_for_timeout(200); print('바깥 눌러 닫힘:', await pg.locator('#ov').count()==0, errs)
        await b.close()
asyncio.run(main())
