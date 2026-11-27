import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844})).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members .ordpair'); await pg.locator('#members .ord:not([disabled]) >> nth=0').click(); await pg.wait_for_timeout(300)
    await pg.evaluate("""() => { const d = JSON.parse(localStorage.getItem('sched84-demo')); const t = new Date().toISOString().slice(0,10), k = d.clients[0], ps = d.profiles.filter(p => p.approved);
      const add = n => { const x = new Date(t); x.setDate(x.getDate() + n); return x.toISOString().slice(0,10); };
      d.events = d.events.filter(e => e.start_date > t || e.end_date < t);
      [[0,2,[ps[0].id, ps[1].id]],[0,5,[ps[2].id]],[1,4,[ps[3].id]]].forEach(([a,b,m], i) => d.events.push({ id: 'dup' + i, owner_id: ps[0].id, type: d.events[0].type, title: k.name, start_date: add(a), end_date: add(b), memo: '', client_id: k.id, members: m, roles: {} }));
      localStorage.setItem('sched84-demo', JSON.stringify(d)); }""")
    await pg.reload(); await pg.wait_for_selector('.grid'); await pg.wait_for_timeout(300)
    print('오늘 칸 칩(같은 거래처 3건):', await pg.evaluate("[...document.querySelectorAll('.cell.today .chip')].map(c=>c.innerText)"))
    await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); print('그날 목록:', await pg.evaluate("[...document.querySelectorAll('.ov.mid .item')].map(i=>i.innerText.replace(/\\n/g,' / '))")); await pg.mouse.click(5,5); await pg.wait_for_timeout(200)
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); await pg.click('.mode button:has-text("거래처별")'); await pg.wait_for_timeout(300)
    print('거래처별 오늘 칸:', await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => r.cells[0].innerText.trim() + ':' + [...r.querySelectorAll('td.tod .chip')].map(c=>c.innerText).join(','))"))
    await pg.locator('table.team td.tod .chip').first.click(); await pg.wait_for_timeout(300); print('겹친 칩 누름 → 그날 목록 열림:', await pg.locator('.ov.mid').count()==1); await pg.mouse.click(5,5); await pg.wait_for_timeout(200)
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#kbox'); print('현재 거래처 색:', await pg.evaluate("JSON.parse(localStorage.getItem('sched84-demo')).clients.map(c=>c.color)"))
    await pg.click('button:has-text("+ 추가")'); await pg.wait_for_selector('.sw.many'); print('새 거래처 기본 색:', await pg.evaluate("document.querySelector('.sw button.on').getAttribute('aria-label')"), errs)
    await b.close()
asyncio.run(main())
