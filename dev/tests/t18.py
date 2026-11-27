import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        bad = lambda: pg.evaluate("(() => { const t = document.body.innerText; return ['false','null','undefined','NaN','[object'].filter(w => t.includes(w)); })()")
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid'); out=[]
        async def chk(name): 
            r = await bad(); out.append((name, r)) if r else None
        await chk('cal'); await pg.locator('.cell:has(.chip)').first.click(); await pg.wait_for_selector('.ov.mid'); await chk('day popup')
        await pg.click('.ov.mid .item >> nth=0'); await pg.wait_for_selector('.dtitle'); await chk('detail')
        await pg.click('.ov.full button:has-text("수정"), .ov.full button:has-text("목록으로")'); await pg.wait_for_timeout(300); await chk('form or list'); await pg.evaluate("document.getElementById('ov') && document.getElementById('ov').remove()")
        await pg.click('.fab'); await pg.wait_for_selector('.sheet form'); await chk('new form'); await pg.click('.sheet button:has-text("취소")')
        await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await chk('team people'); await pg.click('.mode button:has-text("거래처별")'); await pg.wait_for_timeout(200); await chk('team client')
        await pg.click('td.who.k >> nth=0'); await pg.wait_for_selector('.ov.full'); await chk('client detail'); await pg.click('.ov.full button:has-text("닫기")')
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list'); await chk('mine')
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=거래처 관리'); await chk('settings')
        await pg.click('button:has-text("+ 거래처 추가")'); await pg.wait_for_selector('.sw.many'); await chk('client add'); await pg.click('.sheet button:has-text("취소")')
        await pg.click('.card.list button.item >> nth=0'); await pg.wait_for_selector('.sw.many'); await chk('client edit (legacy colour)'); await pg.click('.sheet button:has-text("취소")')
        await pg.click('button:has-text("+ 유형 추가")'); await pg.wait_for_selector('.sw'); await chk('category add'); await pg.click('.sheet button:has-text("취소")')
        await pg.click('.item:has-text("김회계") button:has-text("퇴사 처리")'); await pg.wait_for_selector('#cf'); await chk('leave confirm'); await pg.click('#cf button:has-text("아니오")')
        print('화면별 잘못 찍힌 글자:', out or '없음', '| errs', errs)
        await b.close()
asyncio.run(main())
