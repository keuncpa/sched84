import asyncio, json, base64, time
from playwright.async_api import async_playwright
def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width':390,'height':700}); ver={'v':'2026-11-26.2'}
        async def sup(r): await r.fulfill(status=200, content_type='application/json', body='{}')
        await ctx.route('**/*.supabase.co/**', sup)
        async def vroute(r): await r.fulfill(status=200, content_type='application/json', body=json.dumps(ver))
        await ctx.route('**/version.json*', vroute)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8773/index.html'); await pg.wait_for_selector('.auth'); await pg.wait_for_timeout(3600)
        print('same version -> url:', pg.url)
        ver['v']='2026-11-27.1'
        await pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pg.wait_for_timeout(1500)
        print('new version  -> url:', pg.url); u1=pg.url
        await pg.wait_for_timeout(3800); print('no reload loop:', pg.url==u1, errs)
        await b.close()
asyncio.run(main())
