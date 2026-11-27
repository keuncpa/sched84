import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for scheme in ('light','dark'):
            pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, color_scheme=scheme)).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
            await pg.locator('.cell:has(.chip)').first.click(); await pg.wait_for_selector('.ov.mid .item')
            await pg.click('.ov.mid .item:has-text("A사 중간감사")'); await pg.wait_for_selector('.ov.full')
            box = await pg.locator('.ov.full .sheet').bounding_box()
            print(scheme, 'full screen:', round(box['width']), 'x', round(box['height']), '| text:', (await pg.locator('.ov.full').inner_text()).replace('\n',' | ')[:230])
            await pg.screenshot(path=f's23_detail_{scheme}.png')
            if scheme=='light':
                await pg.click('.ov.full button:has-text("목록으로")'); await pg.wait_for_selector('.ov.mid .item'); print(' back to list OK')
                await pg.click('.ov.mid button:has-text("닫기")'); await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team')
                await pg.click('tbody tr:nth-child(4) .chip >> nth=-1'); await pg.wait_for_selector('.ov.full')
                print(' 남의 개인 일정:', (await pg.locator('.ov.full').inner_text()).replace('\n',' | ')[:200])
                await pg.click('.ov.full button:has-text("닫기")'); print(' closed:', await pg.locator('#ov').count()==0)
            print(' errs', errs)
        await b.close()
asyncio.run(main())
