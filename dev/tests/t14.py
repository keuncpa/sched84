import asyncio, json, base64, time
from playwright.async_api import async_playwright
def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')
jwt = b64({'alg':'HS256','typ':'JWT'})+'.'+b64({'sub':'u1','exp':int(time.time())+3600,'email':'a@b.c','role':'authenticated'})+'.sig'
user={'id':'u1','email':'a@b.c','aud':'authenticated','role':'authenticated'}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        # 데모: 버튼 표시·동작
        pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid'); await pg.click('.upd'); await pg.wait_for_timeout(500)
        print('demo toast:', await pg.locator('#toast').inner_text(), '| button restored:', await pg.locator('.upd').inner_text()); await pg.locator('header').screenshot(path='s22_header.png')
        # 실서버 모드(모의): 남이 추가한 일정이 새로고침으로 반영 + 새 버전이면 앱 교체
        ctx = await b.new_context(viewport={'width':390,'height':844}); today=time.strftime('%Y-%m-%d')
        events=[{'id':'ev1','owner_id':'u1','type':'field','title':'기존 일정','start_date':today,'end_date':today,'memo':'','event_members':[]}]; ver={'v':None}
        async def route(r):
            u=r.request.url; body={}
            if '/auth/v1/token' in u: body={'access_token':jwt,'token_type':'bearer','expires_in':3600,'expires_at':int(time.time())+3600,'refresh_token':'r1','user':user}
            elif '/auth/v1/user' in u: body=user
            elif '/rest/v1/profiles' in u: body=[{'id':'u1','name':'상무A','title':'','approved':True,'is_admin':True}]
            elif '/rest/v1/categories' in u: body=[]
            elif '/rest/v1/events' in u: body=events
            await r.fulfill(status=200, content_type='application/json', body=json.dumps(body))
        await ctx.route('**/*.supabase.co/**', route)
        async def vroute(r):
            if ver['v'] is None: await r.continue_()
            else: await r.fulfill(status=200, content_type='application/json', body=json.dumps(ver))
        await ctx.route('**/version.json*', vroute)
        pg2 = await ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)))
        await pg2.goto('http://localhost:8772/index.html'); await pg2.wait_for_selector('.auth'); await pg2.fill('input[type=email]','a@b.c'); await pg2.fill('input[type=password]','secret1'); await pg2.click('button[type=submit]'); await pg2.wait_for_selector('.grid')
        c0 = await pg2.locator('.cell .chip').count()
        events.append({'id':'ev2','owner_id':'u1','type':'leave','title':'남이 방금 넣은 일정','start_date':today,'end_date':today,'memo':'','event_members':[]})
        await pg2.click('.upd'); await pg2.wait_for_timeout(700)
        print('live: chips', c0, '->', await pg2.locator('.cell .chip').count(), '| toast:', await pg2.locator('#toast').inner_text(), '| url:', pg2.url.split('/')[-1])
        ver['v']='2099-01-01.1'; await pg2.click('.upd'); await pg2.wait_for_timeout(600); print('  toast:', await pg2.locator('#toast').inner_text()); await pg2.wait_for_timeout(4000)
        print('new version → reloaded url:', pg2.url.split('/')[-1][:40], errs)
        await b.close()
asyncio.run(main())
