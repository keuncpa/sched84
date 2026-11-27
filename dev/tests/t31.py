import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name, vp in (('폰', {'width':390,'height':844}), ('PC', {'width':1280,'height':860})):
        pg = await (await b.new_context(viewport=vp)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); await pg.click('.ov.mid .item >> nth=0'); await pg.wait_for_selector('.dtitle')
        tb = await pg.locator('.tabs').bounding_box(); ft = await pg.locator('.dfoot').bounding_box() if await pg.locator('.dfoot').count() else None
        top = await pg.evaluate("(()=>{const r=document.querySelector('.tabs button:nth-child(4)').getBoundingClientRect(); return document.elementFromPoint(r.x+r.width/2, r.y+r.height/2).closest('.tabs') ? 'tab' : 'covered'})()")
        print(name, '상세 화면에서 탭 바:', top, '| 아래 버튼이 탭 바에 안 가림:', ft is None or ft['y']+ft['height'] <= tb['y']+1)
        await pg.screenshot(path=f's44_tabs_{name}.png')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_timeout(300); print('  설정 탭 누름 → 상세 닫힘:', await pg.locator('.ov').count()==0, '| 탭:', (await pg.locator('.tabs button.on').inner_text()).strip())
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('tbody .chip >> nth=0'); await pg.wait_for_selector('.dtitle')
        if await pg.locator('.ov.full button.person, .ov.full .dsec button').count(): 
            await pg.locator('.ov.full .dsec button >> nth=0').click(); await pg.wait_for_timeout(300)
        await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid'); print('  거래처/상세 → 달력 탭:', await pg.locator('.ov').count()==0, (await pg.locator('.tabs button.on').inner_text()).strip())
        # 삭제 확인 창은 탭 바보다 위
        await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); await pg.click('.ov.mid .item >> nth=0'); await pg.wait_for_selector('.dtitle')
        if await pg.locator('.dfoot button:has-text("삭제")').count():
            await pg.click('.dfoot button:has-text("삭제")'); await pg.wait_for_selector('#cf'); print('  확인 창이 탭 바 위:', await pg.evaluate("(()=>{const r=document.querySelector('.tabs button:nth-child(1)').getBoundingClientRect(); return !!document.elementFromPoint(r.x+r.width/2, r.y+r.height/2).closest('#cf')})()"))
        print('  errs', errs)
    await b.close()
asyncio.run(main())
