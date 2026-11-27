import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for sysmode in ('dark','light'):
        ctx = await b.new_context(viewport={'width':390,'height':844}, color_scheme=sysmode); pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
        bg = lambda: pg.evaluate("[getComputedStyle(document.body).backgroundColor, getComputedStyle(document.querySelector('.card')).backgroundColor, getComputedStyle(document.querySelector('.chip')||document.body).backgroundColor, document.documentElement.style.colorScheme, document.querySelector('meta[name=theme-color]').content].join(' | ')")
        print(f'[폰 설정 {sysmode}] 기본(시스템):', await bg())
        await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#theme')
        for label in ('밝게','어둡게','시스템 설정'):
            await pg.click(f'#theme button:has-text("{label}")'); await pg.wait_for_timeout(150); await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid')
            print(f'   {label}:', await bg()); 
            if label=='어둡게' and sysmode=='light': await pg.screenshot(path='s45_forced_dark.png')
            if label=='밝게' and sysmode=='dark': await pg.screenshot(path='s45_forced_light.png')
            await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#theme')
        await pg.click('#theme button:has-text("밝게")' if sysmode=='dark' else '#theme button:has-text("어둡게")'); await pg.reload(); await pg.wait_for_selector('.grid'); print('   다시 열어도 유지:', await bg(), errs)
    await b.close()
asyncio.run(main())
