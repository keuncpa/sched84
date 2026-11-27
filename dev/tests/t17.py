import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for scheme in ('light','dark'):
            pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, color_scheme=scheme)).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
            await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('text=거래처 관리')
            await pg.click('button:has-text("+ 거래처 추가")'); await pg.wait_for_selector('.sw.many')
            print(scheme, 'swatches:', await pg.locator('.sw.many button').count(), '| 기본 선택:', await pg.locator('.sw.many button.on').get_attribute('aria-label'))
            await pg.locator('.sheet').screenshot(path=f's28_palette_{scheme}.png')
            if scheme=='light':
                # 거래처 6곳을 서로 다른 색으로 추가 → 달력에서 색: 거래처
                await pg.click('.sheet button:has-text("취소")')
                for nm, col in [('가나상사','s340'),('다라전자','h200'),('마바건설','s120'),('사아물산','h40'),('자차화학','s260'),('카타유통','h300')]:
                    await pg.click('button:has-text("+ 거래처 추가")'); await pg.wait_for_selector('.sw.many'); await pg.fill('.sheet input[type=text]', nm); await pg.click(f'.sw.many button.c-{col}'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(350)
                print(' 거래처 목록 색:', await pg.evaluate("[...document.querySelectorAll('.card.list .item')].filter(i=>i.querySelector('i.dot') && !i.querySelector('.ord')).map(i=>i.querySelector('.tt').innerText.replace(/\\n/g,'')+':'+i.querySelector('i.dot').className.replace('dot ',''))"))
                dots = await pg.evaluate("[...document.querySelectorAll('.card.list .item i.dot')].slice(0,10).map(d=>getComputedStyle(d).backgroundColor)"); print(' 점 색 서로 다름:', len(set(dots)), '/', len(dots))
                await pg.click('button:has-text("+ 거래처 추가")'); await pg.wait_for_selector('.sw.many'); print(' 다음 기본색(안 쓰인 색):', await pg.locator('.sw.many button.on').get_attribute('aria-label'), '| 사용 중 표시:', await pg.evaluate("[...document.querySelectorAll('.sw.many button')].filter(b=>b.innerText==='·').length")); await pg.click('.sheet button:has-text("취소")')
                # 일정에 지정 후 달력 확인
                await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid')
                for nm in ['가나상사','마바건설','자차화학']:
                    await pg.click('.fab'); await pg.wait_for_selector('.sheet form'); await pg.fill('.sheet input[type=text]', nm+' 감사'); await pg.select_option('select.inp', label=nm); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(350)
                await pg.wait_for_timeout(200)
                await pg.locator('.cell.today').click(); await pg.wait_for_selector('.ov.mid .item'); await pg.screenshot(path='s29_cal_many_colors.png')
                print(' 오늘 칩 클래스:', await pg.evaluate("[...document.querySelectorAll('.cell.today .chip')].map(c=>c.className)"))
            print(' errs', errs)
        await b.close()
asyncio.run(main())
