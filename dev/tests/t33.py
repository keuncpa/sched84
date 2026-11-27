import asyncio, json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844})).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    # 데모 자료에 미가입 자리(pending)·가입 대기·옮긴 일정을 끼워 넣음
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members .ordpair'); await pg.locator('#members .ord:not([disabled]) >> nth=0').click(); await pg.wait_for_timeout(300); key='sched84-demo'
    await pg.evaluate("""k => { const d = JSON.parse(localStorage.getItem(k)); const me = d.profiles[0].id;
      d.profiles.push({id:'ph1', name:'신승후', title:'', approved:true, is_admin:false, pending:true, sort:15});
      d.profiles.push({id:'new1', name:'신승후', title:'', approved:false, is_admin:false});
      const t = new Date().toISOString().slice(0,10);
      d.events.push({id:'imp1', owner_id: me, type: d.events[0].type, title:'동방 내부회계', start_date:t, end_date:t, memo:'', client_id:null, source:'excel-2611', members:['ph1'], roles:{ph1:'인차지'}});
      localStorage.setItem(k, JSON.stringify(d)); }""", key)
    await pg.reload(); await pg.wait_for_selector('.grid')
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members')
    rows = lambda: pg.evaluate("[...document.querySelectorAll('#members .item')].map(r => r.innerText.replace(/\\n/g,' ').replace(/▲|▼/g,'').trim())")
    print('구성원 줄:', await rows())
    await pg.screenshot(path='s46_link.png')
    await pg.select_option('select[aria-label="신승후 기존 이름과 연결"]', 'ph1'); await pg.wait_for_selector('#cf'); print('확인 창:', (await pg.locator('#cf').inner_text()).replace('\n',' | ')[:170])
    await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(500); print('연결 뒤:', await rows())
    d = await pg.evaluate("k => { const d = JSON.parse(localStorage.getItem(k)); const e = d.events.find(x => x.id==='imp1'); return [e.members, e.roles, d.profiles.filter(p=>p.name==='신승후').map(p=>[p.id,p.approved,p.pending,p.sort])] }", key); print('자료:', d)
    await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid'); await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); await pg.click('.ov.mid .item:has-text("동방")'); await pg.wait_for_selector('.dtitle')
    print('상세:', (await pg.locator('.ov.full .sheet').inner_text()).replace('\n',' | ')[:230]); print('errs', errs)
    await b.close()
asyncio.run(main())
