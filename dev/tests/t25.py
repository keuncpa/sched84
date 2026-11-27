import asyncio, json, base64, time
from playwright.async_api import async_playwright
def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')
jwt = b64({'alg':'HS256','typ':'JWT'})+'.'+b64({'sub':'u1','exp':int(time.time())+3600,'email':'a@b.c','role':'authenticated'})+'.sig'
user={'id':'u1','email':'a@b.c','aud':'authenticated','role':'authenticated'}
profiles=[{'id':'u1','name':'상무A','title':'상무','approved':True,'is_admin':True},{'id':'u2','name':'팀원B','title':'','approved':True,'is_admin':False}]
DELAY=1.5
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = await b.new_context(viewport={'width':390,'height':844}); today=time.strftime('%Y-%m-%d')
    events=[{'id':'ev1','owner_id':'u1','type':'field','title':'A사 중간감사','start_date':today,'end_date':today,'memo':'','event_members':[{'user_id':'u1'},{'user_id':'u2'}]}]
    state={'fail':False,'n':0}
    async def route(r):
        u=r.request.url; m=r.request.method; body={}; status=200
        if '/rest/v1/' in u: state['n']+=1; await asyncio.sleep(DELAY)       # 느린 서버 흉내
        if state['fail'] and '/rest/v1/events' in u: return await r.abort()
        if '/auth/v1/token' in u: body={'access_token':jwt,'token_type':'bearer','expires_in':3600,'expires_at':int(time.time())+3600,'refresh_token':'r1','user':user}
        elif '/auth/v1/user' in u: body=user
        elif '/rest/v1/profiles' in u: body=profiles
        elif '/rest/v1/categories' in u or '/rest/v1/clients' in u: body=[]
        elif '/rest/v1/events' in u and m=='GET': body = events if 'client_id' in u else [{'id':'ev1','event_members':[{'user_id':'u1'}]}]
        elif '/rest/v1/rpc/' in u: body=None
        await r.fulfill(status=status, content_type='application/json', body=json.dumps(body))
    await ctx.route('**/*.supabase.co/**', route)
    pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8772/index.html'); await pg.wait_for_selector('.auth')
    await pg.fill('input[type=email]','a@b.c'); await pg.fill('input[type=password]','secret1'); await pg.click('button[type=submit]')
    await pg.wait_for_selector('.grid .chip', timeout=20000)
    await pg.click('.tabs button:nth-child(3)'); await pg.wait_for_timeout(150); print(' 미리 받기 전 내 일정 첫 화면:', (await pg.locator('main .card').inner_text())[:20]); await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_timeout(5000)
    async def sw(n, sel, label):
        t=time.time(); await pg.click(f'.tabs button:nth-child({n})'); await pg.wait_for_selector(sel); ms=int((time.time()-t)*1000)
        chips = await pg.locator('main .chip, main .item').count(); bz = await pg.evaluate("document.querySelector('header').classList.contains('busy')")
        print(f' {label}: {ms}ms 만에 화면 전환 | 내용 {chips}개 바로 보임 | 받아오는 중 표시: {bz}')
    print(f'서버 응답 {DELAY}초 지연 상태에서:')
    await sw(2,'table.team','팀 보기(첫 방문, 미리 받아둠)'); await sw(3,'.card','내 일정(첫 방문, 미리 받아둠)'); await sw(1,'.grid','달력(재방문)'); await sw(2,'table.team','팀 보기(재방문)')
    await pg.wait_for_timeout(2200); print(' 응답 도착 후 표시줄 꺼짐:', not await pg.evaluate("document.querySelector('header').classList.contains('busy')"), '| 칩:', await pg.locator('table.team .chip').count())
    # 빠르게 연타해도 마지막 탭이 유지되는지
    for n in (1,2,3,4,1,3): await pg.click(f'.tabs button:nth-child({n})')
    await pg.wait_for_timeout(2500); print(' 연타 후 선택된 탭:', await pg.locator('.tabs button.on').inner_text(), '| 화면:', (await pg.locator('main').inner_text())[:40].replace('\n',' / '))
    # 다음 달(처음 보는 범위): 틀은 즉시, 내용은 도착 후
    await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid'); t=time.time()
    title0 = await pg.locator('.mtitle, .nav b, .bar b').first.inner_text() if await pg.locator('.mtitle, .nav b, .bar b').count() else ''
    # 설정에서 입력 중인 글자가 뒤늦은 응답에 지워지지 않는지
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('main input'); inp = pg.locator('main input[type=text]').first
    await inp.fill('입력중인이름'); await pg.wait_for_timeout(2500); print(' 설정: 응답 도착 후에도 입력값 유지:', await inp.input_value()=='입력중인이름')
    # 서버 오류 시: 화면은 그대로, 안내만
    state['fail']=True; state['n']=0; await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.wait_for_timeout(12000)
    print(' 조회 실패 시 기존 내용 유지:', await pg.locator('table.team .chip').count(), '개 | 안내:', (await pg.locator('.toast').inner_text()) if await pg.locator('.toast').count() else '', '| 표시줄 꺼짐:', not await pg.evaluate("document.querySelector('header').classList.contains('busy')"))
    print(' 실패 중 요청 수:', state['n']); await pg.wait_for_timeout(25000); print(' 25초 더 뒤: 요청', state['n'], '| 표시줄 꺼짐:', not await pg.evaluate("document.querySelector('header').classList.contains('busy')"), '| toast:', await pg.evaluate("document.querySelector('.toast')?.innerText"))
    print(' errs', errs); await b.close()
asyncio.run(main())
