import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for scheme in ('dark','light'):
            pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, color_scheme=scheme)).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
            chips = await pg.evaluate("[...document.querySelectorAll('.cell .chip')].map(c => c.innerText.split(' ').slice(-2).join(' ') + ' → ' + c.className.replace('chip fill ',''))")
            print(scheme, '기본 색 기준 버튼:', await pg.locator('.fchip >> nth=0').inner_text(), '| 칩 색 종류:', sorted(set(c.split(' → ')[1] for c in chips)))
            print('  예:', sorted(set(chips))[:7])
            await pg.locator('.cell:has(.chip)').first.click(); await pg.wait_for_selector('.ov.mid .item')
            print('  목록 항목:', await pg.evaluate("[...document.querySelectorAll('.ov.mid .item')].map(i => [...i.querySelector('.tt').childNodes].map(n => n.nodeType===1 ? '['+n.innerText+']' : n.textContent).join('') + ' / 태그: ' + [...i.querySelectorAll('.tags .badge')].map(x=>x.innerText).join(','))"))
            await pg.screenshot(path=f's32_client_first_{scheme}.png')
            await pg.click('.ov.mid .item >> nth=1'); await pg.wait_for_selector('.dtitle'); print('  상세 제목:', (await pg.locator('.dtitle').inner_text()).replace('\n',' '))
            if scheme=='dark': await pg.screenshot(path='s33_detail_client_first.png')
            await pg.evaluate("document.getElementById('ov').remove()")
            await pg.click('.fchip:has-text("색: 거래처")'); await pg.wait_for_timeout(200)
            print('  유형 색으로 전환:', await pg.locator('.fchip >> nth=0').inner_text(), sorted(set(await pg.evaluate("[...document.querySelectorAll('.cell .chip')].map(c => c.className.replace('chip fill ',''))"))), errs)
        await b.close()
asyncio.run(main())
