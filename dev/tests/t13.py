import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list')
        n0 = await pg.locator('.item').count()
        # 1) 삭제 → 확인 창 → 아니오: 그대로
        await pg.click('.item >> nth=0'); await pg.click('.sheet .btn.danger'); await pg.wait_for_selector('#cf')
        print('dialog:', (await pg.locator('#cf').inner_text()).replace('\n',' | ')); await pg.screenshot(path='s21_confirm.png')
        await pg.click('#cf button:has-text("아니오")'); await pg.wait_for_timeout(200)
        print('아니오 → 창 닫힘:', await pg.locator('#cf').count()==0, '| 상세창 유지:', await pg.locator('#ov').count()==1)
        await pg.click('.sheet button:has-text("닫기")'); print('count unchanged:', await pg.locator('.item').count()==n0)
        # 2) 삭제 → 묻지 않기 체크 + 예: 삭제됨
        await pg.click('.item >> nth=0'); await pg.click('.sheet .btn.danger'); await pg.check('#cfskip'); await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(400)
        n1 = await pg.locator('.item').count(); print('예 → 삭제됨:', n1==n0-1)
        # 3) 다음부터는 바로 삭제
        await pg.click('.item >> nth=0'); await pg.click('.sheet .btn.danger'); await pg.wait_for_timeout(400)
        print('다음부터 확인 없이 바로 삭제:', await pg.locator('#cf').count()==0 and await pg.locator('.item').count()==n1-1)
        # 4) 설정에서 다시 켜기
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#askdel'); print('설정 스위치 상태(꺼짐):', not await pg.is_checked('#askdel'))
        await pg.check('#askdel'); await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list')
        await pg.click('.item >> nth=0'); await pg.click('.sheet .btn.danger'); await pg.wait_for_timeout(300); print('다시 켜면 확인 창 표시:', await pg.locator('#cf').count()==1)
        await pg.mouse.click(5,5); await pg.wait_for_timeout(200); print('바깥 누르면 취소:', await pg.locator('#cf').count()==0 and await pg.locator('.item').count()==n1-1, errs)
        await b.close()
asyncio.run(main())
