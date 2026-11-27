import asyncio, json, base64, time, re
from playwright.async_api import async_playwright
def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')
jwt = b64({'alg':'HS256','typ':'JWT'})+'.'+b64({'sub':'u1','exp':int(time.time())+3600,'email':'a@b.c','role':'authenticated'})+'.sig'
user={'id':'u1','email':'a@b.c','aud':'authenticated','role':'authenticated'}
profiles=[{'id':'u1','name':'상무A','title':'상무','approved':True,'is_admin':True},{'id':'u2','name':'팀원B','title':'','approved':True,'is_admin':False},{'id':'u3','name':'팀원C','title':'','approved':True,'is_admin':False}]
async def run(b, admin):
    ctx = await b.new_context(viewport={'width':390,'height':844}); calls=[]
    today=time.strftime('%Y-%m-%d')
    events=[{'id':'ev1','owner_id':'u1','type':'field','title':'A사 중간감사','start_date':today,'end_date':today,'memo':'','event_members':[{'user_id':'u2'},{'user_id':'u3'}]},
            {'id':'ev2','owner_id':'u2','type':'leave','title':'연차','start_date':today,'end_date':today,'memo':'','event_members':[]}]
    me = 'u1' if admin else 'u2'
    async def route(r):
        u=r.request.url; m=r.request.method; path=u.split('.co')[1]
        calls.append((m, path[:150], (r.request.post_data or '')[:200])); body={}; status=200
        if '/auth/v1/token' in u: body={'access_token':jwt.replace('u1',me),'token_type':'bearer','expires_in':3600,'expires_at':int(time.time())+3600,'refresh_token':'r1','user':{**user,'id':me}}
        elif '/auth/v1/user' in u: body={**user,'id':me}
        elif '/rest/v1/profiles' in u: body=profiles
        elif '/rest/v1/events' in u and m=='GET':
            body = events if 'client_id' in u else [{'id':'ev1','event_members':[{'user_id':me}]}]
        elif '/rest/v1/events' in u and m=='POST': body=[{'id':'new1'}]; status=201
        elif '/rest/v1/events' in u and m=='PATCH': body=[{'id':'ev1'}]
        elif '/rest/v1/event_members' in u: body=[]; status=201 if m=='POST' else 200
        elif '/functions/v1/notify' in u: body={'sent':2,'failed':0,'devices':2}
        elif '/rest/v1/rpc/' in u: body=None
        await r.fulfill(status=status, content_type='application/json', body=json.dumps(body))
    await ctx.route('**/*.supabase.co/**', route)
    pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    # 로그인 세션을 미리 심어 둠
    await pg.goto('http://localhost:8772/index.html'); await pg.wait_for_selector('.auth')
    await pg.fill('input[type=email]','a@b.c'); await pg.fill('input[type=password]','secret1'); await pg.click('button[type=submit]')
    await pg.wait_for_selector('.grid', timeout=15000)
    # jwt sub는 가짜라 S.user.id 는 token 응답의 user.id
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team')
    rows = await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => [r.cells[0].innerText.split('\\n')[0], [...new Set([...r.querySelectorAll('.chip')].map(c => c.innerText))].join('|')])")
    print(' team rows:', rows)
    await pg.click('tbody .chip:has-text("A사 중간감사") >> nth=0'); await pg.wait_for_selector('.sheet')
    btns = await pg.evaluate("[...document.querySelectorAll('.sheet .btns button')].map(b=>b.innerText)")
    print(' 배정 일정 버튼:', btns, '|', (await pg.locator('.sheet .help').inner_text()) if await pg.locator('.sheet .help').count() else '')
    await pg.click('.sheet button:has-text("닫기")')
    await pg.click('.fab'); await pg.wait_for_selector('.sheet form')
    print(' 배정 선택란 표시:', await pg.locator('.pick').count())
    if admin:
        calls.clear()
        await pg.fill('.sheet input[type=text]', 'F사 기말감사'); await pg.click('.pick button:has-text("팀원B")'); await pg.click('.pick button:has-text("팀원C")')
        await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(1200)
        for c in calls:
            if c[0] in ('POST','PATCH','DELETE'): print('   ', c[0], c[1].split('?')[0], c[2][:150])
        print(' toast:', await pg.locator('#toast').inner_text())
        # 기존 배정 일정 수정: C 해제 + 날짜 변경 → DELETE members + update 알림(B)
        calls.clear()
        await pg.click('tbody .chip:has-text("A사 중간감사") >> nth=0'); await pg.click('.sheet button:has-text("수정")'); await pg.wait_for_selector('.pick')
        await pg.click('.pick button:has-text("팀원C")'); await pg.fill('.sheet input[type=text]', 'A사 중간감사(변경)'); await pg.click('.sheet button[type=submit]'); await pg.wait_for_timeout(1200)
        for c in calls:
            if c[0] in ('POST','PATCH','DELETE'): print('   ', c[0], re.sub(r'%2C',',',c[1])[:110], c[2][:120])
    else:
        await pg.click('.sheet button:has-text("취소")')
        await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_selector('.list')
        print(' mine:', await pg.evaluate("[...document.querySelectorAll('.item')].map(i => i.innerText.replace(/\\n/g,' / '))"))
        q=[c[1] for c in calls if 'inner' in c[1]]; print(' 배정 조회 쿼리:', q[-1][:140] if q else None)
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_timeout(800)
    t = await pg.locator('main').inner_text(); i=t.find('배정 알림'); print(' 알림 카드:', t[i:i+75].replace('\n',' / '), '| stray:', 'false' in t or 'null' in t, errs)
    if admin: await pg.screenshot(path='s15_settings_live.png', full_page=True)
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for a in (True, False): print('=== 관리자' if a else '=== 일반 팀원'); await run(b,a)
        await b.close()
asyncio.run(main())
