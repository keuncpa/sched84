import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        iphone = p.devices['iPhone 13']
        ctx = await b.new_context(**{k:v for k,v in iphone.items() if k not in ('default_browser_type',)}, color_scheme='dark')
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        await pg.click('.fab'); await pg.wait_for_selector('.sheet form')
        print('필드 순서:', await pg.evaluate("[...document.querySelectorAll('.sheet form > label')].map(l => l.innerText)"))
        print('거래처 선택 전 제목 예시:', await pg.get_attribute('.sheet input[type=text]', 'placeholder'))
        await pg.select_option('select.inp', label='B사'); print('거래처 선택 후 제목 예시:', await pg.get_attribute('.sheet input[type=text]', 'placeholder'))
        vw = pg.viewport_size['width']
        boxes = await pg.evaluate("[...document.querySelectorAll('.sheet input[type=date]')].map(i => { const r = i.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right)]; })")
        print('날짜 칸 좌우 위치:', boxes, '/ 화면 폭', vw, '→ 화면 안에 들어옴:', all(r <= vw for _, r in boxes))
        await pg.screenshot(path='s37_form_order.png')
        await pg.fill('.sheet input[type=text]', '기말감사'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(400)
        print('저장 후 오늘 칩:', await pg.evaluate("[...document.querySelectorAll('.cell.today .chip')].map(c => c.innerText.replace(/\\n/g,' / '))"), errs)
        await b.close()
asyncio.run(main())
