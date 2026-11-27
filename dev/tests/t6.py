import asyncio, json, base64, time
from playwright.async_api import async_playwright
def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')
jwt = b64({'alg':'HS256','typ':'JWT'})+'.'+b64({'sub':'u1','exp':int(time.time())+3600,'email':'a@b.c','role':'authenticated'})+'.sig'
user={'id':'u1','email':'a@b.c','aud':'authenticated','role':'authenticated'}
async def run(b, keep):
    ctx = await b.new_context(viewport={'width':390,'height':700})
    async def route(r):
        u=r.request.url
        if '/auth/v1/token' in u: body={'access_token':jwt,'token_type':'bearer','expires_in':3600,'expires_at':int(time.time())+3600,'refresh_token':'r1','user':user}
        elif '/auth/v1/user' in u: body=user
        elif '/rest/v1/profiles' in u: body=[{'id':'u1','name':'테스트','title':'','approved':True,'is_admin':True}]
        elif '/rest/v1/events' in u: body=[]
        else: body={}
        await r.fulfill(status=200, content_type='application/json', body=json.dumps(body))
    await ctx.route('**/*.supabase.co/**', route)
    pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8770/index.html'); await pg.wait_for_selector('.auth')
    print(' default checked:', await pg.is_checked('#keep'))
    if not keep: await pg.uncheck('#keep')
    await pg.fill('input[type=email]','a@b.c'); await pg.fill('input[type=password]','secret1'); await pg.click('button[type=submit]')
    await pg.wait_for_selector('.grid', timeout=15000)
    st = await pg.evaluate("({ls:Object.keys(localStorage).filter(k=>k.includes('auth-token')).length, ss:Object.keys(sessionStorage).filter(k=>k.includes('auth-token')).length})")
    print(' keep=%s token in localStorage=%s sessionStorage=%s'%(keep, st['ls'], st['ss']))
    await pg.reload(); await pg.wait_for_selector('.grid', timeout=15000); print(' reload stays logged in: True')
    # simulate app closed & reopened: new page in same context (sessionStorage is per-tab)
    pg2 = await ctx.new_page(); await pg2.goto('http://localhost:8770/index.html'); await pg2.wait_for_timeout(2500)
    print(' reopen ->', 'calendar' if await pg2.locator('.grid').count() else 'login screen', '| keep box now:', (await pg2.is_checked('#keep')) if await pg2.locator('#keep').count() else '-', errs)
    if not keep: await pg2.screenshot(path='s10_login.png')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for k in (True, False): print('case keep =',k); await run(b,k)
        await b.close()
asyncio.run(main())
