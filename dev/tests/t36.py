import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8771/index.html'); await pg.wait_for_selector('.grid')
    await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#members .ordpair'); await pg.locator('#members .ord:not([disabled]) >> nth=0').click(); await pg.wait_for_timeout(300)
    await pg.evaluate("""() => { const d = JSON.parse(localStorage.getItem('sched84-demo')); const t = new Date().toISOString().slice(0,10);
      for (let i = 0; i < 8; i++) d.profiles.push({ id: 'L' + i, name: '퇴사자' + (i + 1), title: '', approved: false, is_admin: false, left_at: '2026-0' + (i + 1) + '-15T00:00:00Z' });
      d.events.push({ id: 'old1', owner_id: d.profiles[0].id, type: d.events[0].type, title: '옛 일정', start_date: t, end_date: t, memo: '', client_id: null, members: ['L2', d.profiles[0].id], roles: {} });
      localStorage.setItem('sched84-demo', JSON.stringify(d)); }""")
    await pg.reload(); await pg.wait_for_selector('.grid'); await pg.click('.tabs button:nth-child(4)'); await pg.wait_for_selector('#leftbox')
    names = lambda: pg.evaluate("[...document.querySelectorAll('#leftbox .item .tt')].map(x => x.firstChild.textContent)")
    bb = await pg.locator('#leftbox').bounding_box(); print('퇴사자 목록 높이:', round(bb['height']), '| 줄:', await names(), '| 버튼:', await pg.evaluate("[...new Set([...document.querySelectorAll('#leftbox button')].map(b=>b.innerText))]"))
    await pg.locator('#leftbox').scroll_into_view_if_needed(); await pg.screenshot(path='s48_left.png')
    await pg.click('button[aria-label="퇴사자3 삭제"]'); await pg.wait_for_selector('#cf'); print('확인 창:', (await pg.locator('#cf').inner_text()).replace('\n',' | ')[:150]); await pg.click('#cf button:has-text("예")'); await pg.wait_for_timeout(400)
    print('삭제 뒤:', await names(), '| 제목:', await pg.evaluate("[...document.querySelectorAll('main h2')].map(h=>h.innerText).find(t=>t.startsWith('퇴사자'))"))
    await pg.click('.tabs button:nth-child(1)'); await pg.wait_for_selector('.grid'); await pg.click('.cell.today'); await pg.wait_for_selector('.ov.mid'); await pg.click('.ov.mid .item:has-text("옛 일정")'); await pg.wait_for_selector('.dtitle')
    print('과거 일정 상세:', (await pg.locator('.ov.full .sheet').inner_text()).replace('\n',' | ')[:160])
    await pg.click('.tabs button:nth-child(2)'); await pg.wait_for_selector('table.team'); print('팀 보기 줄:', await pg.evaluate("[...document.querySelectorAll('table.team tbody tr')].map(r => r.cells[0].innerText.replace(/\\n/g,' '))"), errs)
    await b.close()
asyncio.run(main())
