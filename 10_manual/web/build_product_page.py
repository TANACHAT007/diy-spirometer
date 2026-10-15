"""Builds product_page.html (soft 3D-cartoon style) from product_page.src.html + restyle_soft3d.css + draw_soft3d.js."""
import base64, os, re
H = os.path.dirname(os.path.abspath(__file__))
rd = lambda n: open(os.path.join(H, n), encoding='utf-8').read()
DASH = 'https://claude.ai/artifact/B3oUdVf87wnw9oiRZ8fzzU'
s = rd('product_page.src.html')
a = s.index('<link rel="preconnect"'); b = s.index('</style>') + len('</style>')
s = s[:a] + rd('restyle_soft3d.css') + s[b:]
a = s.index('function draw(now){'); b = s.index('function readouts(){')
s = s[:a] + rd('draw_soft3d.js') + '\n' + s[b:]
s = s.replace('css("--blue")', 'css("--sky-d")')
s = s.replace('<button class="wait" disabled title="เปิดใช้เร็วๆ นี้">เข้าใช้งาน</button>', f'<a class="go" href="{DASH}" target="_blank" rel="noopener">เข้าใช้งาน</a>')
s = s.replace('<button class="btn ghost wait" id="goApp" disabled aria-describedby="goNote">เข้าหน้าเว็บใช้งาน · เร็วๆ นี้</button>',
              f'<a class="btn ghost" id="goApp" href="{DASH}" target="_blank" rel="noopener" aria-describedby="goNote">เข้าหน้าเว็บใช้งาน</a>')
s = s.replace('แดชบอร์ดผู้ป่วย/ครู-แพทย์ เปิดใช้เมื่อเชื่อมต่อฐานข้อมูลเสร็จ',
              'เปิดแดชบอร์ดได้แล้ว ตอนนี้แสดงข้อมูลตัวอย่าง จะรับผลจริงเมื่อเชื่อมต่อฐานข้อมูลและมีเครื่องส่งข้อมูล')
s = s.replace('<span class="k">A / C</span>', '<span class="k dk">A / C</span>').replace('<span class="k">IoT</span>', '<span class="k dk">IoT</span>')
s = s.replace('<span class="k">Dock</span>', '<span class="k dk">Dock</span>')
s = s.replace('<a href="#spec">สเปก</a>', '<a href="#spec">สเปก</a>', 1)
# nav entry button gets the primary look
s = s.replace(f'<a class="go" href="{DASH}"', f'<a class="go" href="{DASH}"')
s = s.replace('<a class="btn ghost" href="#view">ดูภายในเครื่อง</a></div>',
  '<a class="btn ghost" href="#view">ดูภายในเครื่อง</a><a class="btn ghost" id="goApp" href="'+DASH+'" target="_blank" rel="noopener" aria-describedby="goNote">เข้าหน้าเว็บใช้งาน</a></div><p class="note" id="goNote">เปิดแดชบอร์ดได้แล้ว ตอนนี้แสดงข้อมูลตัวอย่าง จะรับผลจริงเมื่อเชื่อมต่อฐานข้อมูลและมีเครื่องส่งข้อมูล</p>')
s = s.replace('<a href="#spec">สเปก</a>', '<a href="#spec">สเปก</a><a class="go" href="'+DASH+'" target="_blank" rel="noopener">เข้าใช้งาน</a>', 1)
uri = lambda n: 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(H, 'img', n + '.jpg'), 'rb').read()).decode()
for k, n in (('HERO', 'cu_hero'), ('OPEN', 'cu_open'), ('INSIDE', 'cu_inside'), ('DOCK', 'cu_dock')):
    s = s.replace('{{' + k + '}}', uri(n))
open(os.path.join(H, 'product_page.html'), 'w', encoding='utf-8').write(s)
print('built', len(s) // 1024, 'KB')
