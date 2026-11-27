import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    # PC
    pg = await (await b.new_context(viewport={'width':1280,'height':900}, accept_downloads=True)).new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#xlbtn')
    print('기간 선택지:', await pg.evaluate("[...document.querySelector('select[aria-label=\"내려받을 기간\"]').options].map(o=>o.text + (o.selected?'*':''))"))
    async with pg.expect_download() as d: await pg.click('#xlbtn')
    dl = await d.value; await dl.save_as('xl/pc_quarter.xlsx'); print('PC 내려받기:', dl.suggested_filename, '| 안내:', await pg.locator('#toast').inner_text())
    await pg.select_option('select[aria-label="내려받을 기간"]', index=7)
    async with pg.expect_download() as d: await pg.click('#xlbtn')
    dl = await d.value; await dl.save_as('xl/pc_year.xlsx'); print('PC 연간:', dl.suggested_filename, errs)
    # 폰(터치) — 공유 기능 있는 경우 / 없는 경우
    for share in (True, False):
        ctx = await b.new_context(viewport={'width':390,'height':844}, has_touch=True, is_mobile=True, accept_downloads=True)
        await ctx.add_init_script("window.__shared=null;" + ("navigator.canShare = d => !!(d && d.files); navigator.share = async d => { window.__shared = d.files.map(f => f.name + ':' + f.size + ':' + f.type); };" if share else "navigator.canShare = undefined; navigator.share = undefined;"))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#xlbtn')
        if share:
            await pg.click('#xlbtn'); await pg.wait_for_selector('.ov.mid'); print('폰(공유 가능) 창:', (await pg.locator('.ov.mid .sheet').inner_text()).replace('\n',' | '))
            await pg.screenshot(path='s40_xl_phone.png')
            await pg.click('.ov.mid button:has-text("저장·공유하기")'); await pg.wait_for_timeout(300); print('  공유로 넘긴 파일:', await pg.evaluate('window.__shared'), '| 창 닫힘:', await pg.locator('.ov').count()==0)
        else:
            async with pg.expect_download() as d: await pg.click('#xlbtn')
            dl = await d.value; print('폰(공유 불가) 바로 내려받기:', dl.suggested_filename, '| 창:', (await pg.locator('.ov.mid .sheet').inner_text()).replace('\n',' | ')[:120])
        print('  errs', errs)
    await b.close()
asyncio.run(main())
