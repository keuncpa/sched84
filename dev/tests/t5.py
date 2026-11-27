import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width':390,'height':700})
        calls=[]
        async def route(r):
            u=r.request.url; calls.append((r.request.method,u.split('.co')[1][:60], (r.request.post_data or '')[:120]))
            if '/auth/v1/recover' in u: await r.fulfill(status=200, content_type='application/json', body='{}')
            elif '/auth/v1/user' in u and r.request.method=='GET': await r.fulfill(status=200, content_type='application/json', body=json.dumps({'id':'u1','email':'a@b.c','aud':'authenticated','role':'authenticated'}))
            elif '/auth/v1/user' in u: await r.fulfill(status=200, content_type='application/json', body=json.dumps({'id':'u1','email':'a@b.c','aud':'authenticated'}))
            elif '/rest/v1/profiles' in u: await r.fulfill(status=200, content_type='application/json', body=json.dumps([{'id':'u1','name':'테스트','title':'','approved':True,'is_admin':True}]))
            elif '/rest/v1/events' in u: await r.fulfill(status=200, content_type='application/json', body='[]')
            else: await r.fulfill(status=200, content_type='application/json', body='{}')
        await ctx.route('**/*.supabase.co/**', route)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8769/index.html'); await pg.wait_for_selector('.auth')
        await pg.click('text=비밀번호를 잊으셨나요?'); await pg.fill('input[type=email]','a@b.c'); await pg.click('button[type=submit]')
        await pg.wait_for_selector('text=메일을 확인해 주세요'); print('reset request OK:', [c for c in calls if 'recover' in c[1]])
        # recovery link landing (implicit flow hash)
        import base64, time
        def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')
        jwt = b64({'alg':'HS256','typ':'JWT'})+'.'+b64({'sub':'u1','exp':int(time.time())+3600,'email':'a@b.c','role':'authenticated'})+'.sig'
        pg2 = await ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)))
        await pg2.goto(f'http://localhost:8769/index.html#access_token={jwt}&expires_in=3600&refresh_token=r1&token_type=bearer&type=recovery')
        await pg2.wait_for_selector('text=새 비밀번호 설정', timeout=15000); print('recovery screen OK')
        await pg2.fill('input >> nth=0','newpass1'); await pg2.fill('input >> nth=1','newpass2'); await pg2.click('button[type=submit]'); await pg2.wait_for_timeout(300)
        print('mismatch toast:', await pg2.locator('#toast').inner_text())
        await pg2.fill('input >> nth=1','newpass1'); await pg2.click('button[type=submit]')
        await pg2.wait_for_selector('.grid', timeout=15000); print('after change -> calendar OK, url:', pg2.url)
        print('PUT user:', [c[:2] for c in calls if c[0]=='PUT'], 'stray text:', 'false' in (await pg2.locator('#app').inner_text()) or 'null' in (await pg2.locator('#app').inner_text()))
        await pg2.screenshot(path='s9_live_shell.png')
        # expired link
        pg3 = await ctx.new_page(); await pg3.goto('http://localhost:8769/index.html#error=access_denied&error_code=otp_expired&error_description=x'); await pg3.wait_for_timeout(1500)
        print('expired toast:', await pg3.locator('#toast').inner_text()); print('errs', errs)
        await b.close()
asyncio.run(main())
