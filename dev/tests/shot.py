import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, locale='ko-KR', timezone_id='Asia/Seoul')
        pg = await ctx.new_page()
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.screenshot(path='s1_cal.png')
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.screenshot(path='s2_team.png')
        # add event via FAB
        await pg.click('.fab'); await pg.wait_for_selector('.sheet')
        await pg.click('.seg button:nth-child(2)')
        await pg.click('.quick button:nth-child(1)')
        await pg.screenshot(path='s3_form.png')
        await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list'); await pg.screenshot(path='s4_mine.png')
        n1 = await pg.locator('.item').count()
        # edit then delete first item
        await pg.click('.item >> nth=0'); await pg.wait_for_selector('.sheet'); await pg.screenshot(path='s5_detail.png')
        await pg.click('.btn.danger'); await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(400)
        n2 = await pg.locator('.item').count()
        print('mine count', n1, '->', n2)
        # other's event read-only
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team')
        await pg.click('tbody tr:nth-child(3) .chip >> nth=0'); await pg.wait_for_selector('.sheet')
        print('others editable buttons:', await pg.locator('.sheet .btn.danger').count())
        await pg.click('.sheet .btn.ghost')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_timeout(300); await pg.screenshot(path='s6_set.png', full_page=True)
        print('errors:', errs)
        await b.close()
asyncio.run(main())
