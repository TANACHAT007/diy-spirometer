# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# Rebuilds the #story section of product_page.src.html: illustrated cards -> click -> big image + details + sources.
import re, pathlib
P = pathlib.Path(__file__).with_name('product_page.src.html')

SKY = '#cfe8fb'; GOLD = '#e2b04a'; TAN = '#cdaa78'; BLUE = '#2a86d4'; DEEP = '#0b3a63'; GREEN = '#4cae7a'; FIRE = '#e0653a'

def svg(body):
    return f'<svg viewBox="0 0 640 400" role="img" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">{body}</svg>'

def txt(x, y, s, size=22, fill=DEEP, anchor='middle', w=700):
    size = round(size * 1.3)
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" font-family="Noto Sans Thai,Sora,sans-serif">{s}</text>'

def smoke(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#7c8793" opacity=".55"/>'

# 1 burning field
a1 = svg(
    '<defs><linearGradient id="s1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fb3c4"/><stop offset="1" stop-color="#e8edf1"/></linearGradient></defs>'
    '<rect width="640" height="400" fill="url(#s1)"/>'
    + ''.join(smoke(x, y, r) for x, y, r in [(250, 150, 46), (300, 100, 58), (370, 70, 66), (450, 50, 70), (200, 190, 36), (520, 90, 52), (130, 215, 28)])
    + f'<path d="M0 290 Q160 250 320 280 T640 262 V400 H0Z" fill="{GOLD}"/>'
    f'<path d="M0 330 Q200 300 420 326 T640 312 V400 H0Z" fill="#c98f2f"/>'
    + ''.join(f'<path d="M{x} 300 q-14 -40 0 -70 q8 24 22 28 q-6 -22 8 -40 q14 38 6 70z" fill="{FIRE}"/><path d="M{x+14} 300 q-6 -24 4 -42 q10 18 6 42z" fill="#ffd27a"/>' for x in (190, 250, 310, 370, 430))
    + ''.join(f'<rect x="{x}" y="340" width="3" height="40" fill="#8a5d12"/>' for x in range(30, 620, 34))
    + txt(320, 388, 'เผาตอซัง · ใบอ้อย · ฟาง', 20, '#ffffff'))

# 2 lungs + PM2.5
def lung(cx, flip):
    s = -1 if flip else 1
    return (f'<path d="M{cx} 130 C{cx+s*10} 120 {cx+s*30} 130 {cx+s*50} 150 C{cx+s*90} 190 {cx+s*100} 260 {cx+s*70} 300 C{cx+s*40} 330 {cx+s*10} 310 {cx+s*6} 270 Z" fill="#f08a8a" stroke="#c75a5a" stroke-width="4"/>'
            f'<path d="M{cx+s*10} 190 l{s*25} 20 M{cx+s*10} 220 l{s*30} 24 M{cx+s*10} 250 l{s*22} 18" stroke="#c75a5a" stroke-width="4" fill="none" stroke-linecap="round"/>')
dots = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#4a5560" opacity=".8"/>' for x, y, r in [(70, 90, 6), (110, 150, 4), (60, 220, 5), (140, 70, 3), (95, 280, 4), (560, 80, 5), (520, 140, 3), (585, 210, 6), (545, 290, 4), (180, 120, 3), (460, 100, 4), (205, 40, 5)])
a2 = svg(f'<rect width="640" height="400" fill="{SKY}"/>'
         '<rect x="308" y="70" width="24" height="95" rx="10" fill="#e9b3b3"/>'
         + lung(300, True) + lung(340, False) + dots
         + txt(320, 360, 'PM2.5 เข้าถึงถุงลม', 24)
         + '<g transform="translate(70 322)">' + txt(0, 0, 'PM2.5', 18, '#4a5560') + '</g>')

# 3 process
def box(x, y, w, h, fill, label, sub=''):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{DEEP}" stroke-width="3"/>'
            + txt(x + w / 2, y + h + 28, label, 18))
def arrow(x1, x2, y=190):
    return f'<path d="M{x1} {y} H{x2} m-10 -10 l10 10 l-10 10" stroke="{DEEP}" stroke-width="4" fill="none" stroke-linecap="round"/>'
straw = ''.join(f'<path d="M{50+i*9} 235 L{70+i*9} 140" stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/>' for i in range(8))
a3 = svg(f'<rect width="640" height="400" fill="#f4f8fc"/>'
         + straw + f'<rect x="48" y="188" width="90" height="12" rx="5" fill="#8a5d12"/>' + txt(95, 270, 'ฟาง/ใบอ้อย', 18)
         + arrow(150, 205)
         + f'<path d="M215 170 h100 v70 q0 22 -22 22 h-56 q-22 0 -22 -22z" fill="#dfc79c" stroke="{DEEP}" stroke-width="3"/><path d="M225 170 q15 -14 30 0 q15 -14 30 0" fill="none" stroke="{DEEP}" stroke-width="3"/>' + txt(265, 300, 'ต้มเป็นเยื่อ', 18)
         + arrow(325, 380)
         + f'<rect x="392" y="140" width="90" height="34" rx="6" fill="{BLUE}"/><rect x="392" y="214" width="90" height="34" rx="6" fill="{BLUE}"/><rect x="418" y="174" width="38" height="40" fill="{TAN}"/>' + txt(437, 300, 'อัดขึ้นรูป', 18)
         + arrow(492, 540)
         + f'<path d="M550 160 h60 v60 h-60z" fill="none"/><ellipse cx="582" cy="190" rx="22" ry="34" fill="{TAN}" stroke="{DEEP}" stroke-width="3"/><ellipse cx="570" cy="190" rx="8" ry="22" fill="#b4916a"/>' + txt(582, 300, 'ที่เป่า', 18)
         + txt(320, 60, 'เศษเหลือทิ้ง → เยื่อ → ขึ้นรูป → ที่เป่าใช้แล้วทิ้ง', 22))

# 4 device
a4 = svg(f'<rect width="640" height="400" fill="#f4f8fc"/>'
         f'<path d="M210 120 h250 q30 0 30 30 v40 q0 20 -20 20 h-60 l-40 140 q-4 14 -18 14 h-40 q-14 0 -10 -16 l26 -138 h-118z" fill="{BLUE}" stroke="{DEEP}" stroke-width="3"/>'
         f'<rect x="205" y="112" width="270" height="22" rx="11" fill="#fff" stroke="{DEEP}" stroke-width="3"/>'
         f'<circle cx="335" cy="250" r="30" fill="{DEEP}" stroke="#fff" stroke-width="4"/>'
         f'<rect x="90" y="132" width="120" height="58" rx="10" fill="{TAN}" stroke="{DEEP}" stroke-width="3"/><ellipse cx="90" cy="161" rx="14" ry="29" fill="#b4916a" stroke="{DEEP}" stroke-width="3"/>'
         f'<path d="M80 105 h-40 m10 -10 l-10 10 l10 10" stroke="{GREEN}" stroke-width="5" fill="none" stroke-linecap="round"/>'
         + txt(20, 90, 'ที่เป่า เปลี่ยนทุกคน', 20, '#5b3a05', 'start')
         + txt(620, 100, 'ท่อวัด ล้างใช้ซ้ำ', 20, DEEP, 'end')
         + txt(320, 380, 'ส่วนที่แม่นยำคงเดิม เปลี่ยนเฉพาะส่วนที่สัมผัสปาก', 20))

# 5 material compare
def disc(cx, color, label, sub):
    return (f'<circle cx="{cx}" cy="170" r="62" fill="{color}" stroke="{DEEP}" stroke-width="3"/>'
            + txt(cx, 280, label, 22) + txt(cx, 310, sub, 17, '#566b82', 'middle', 500))
a5 = svg(f'<rect width="640" height="400" fill="#f4f8fc"/>'
         + disc(120, '#86b8e8', 'PETG', 'ต้นแบบ · พิมพ์ 3 มิติ')
         + disc(320, TAN, 'เยื่อฟาง/ใบอ้อย', 'ขึ้นรูป · ย่อยสลายได้')
         + disc(520, '#e8dcc4', 'กระดาษม้วน', 'แบบ spirometer ทั่วไป')
         + f'<path d="M205 170 h50 m-10 -9 l10 9 l-10 9" stroke="{DEEP}" stroke-width="4" fill="none"/>'
         + txt(320, 60, 'เส้นทางวัสดุของที่เป่า', 24))

# 6 community loop
def node(x, y, label, fill):
    return f'<circle cx="{x}" cy="{y}" r="56" fill="{fill}" stroke="{DEEP}" stroke-width="3"/>' + txt(x, y + 6, label, 14)
a6 = svg(f'<rect width="640" height="400" fill="{SKY}"/>'
         f'<circle cx="320" cy="200" r="125" fill="none" stroke="{DEEP}" stroke-width="4" stroke-dasharray="10 10"/>'
         + node(320, 75, 'ไร่นา', '#f2dc8c') + node(445, 200, 'เยื่อชุมชน', '#e6cfa3') + node(320, 325, 'ที่เป่า', TAN) + node(195, 200, 'ตรวจปอด', '#fff')
         + f'<path d="M370 95 q50 20 70 60 m-8 -14 l8 14 l-14 4" stroke="{DEEP}" stroke-width="4" fill="none"/>'
         + f'<path d="M440 250 q-20 45 -68 62 m10 -2 l-10 2 l6 -12" stroke="{DEEP}" stroke-width="4" fill="none"/>'
         + f'<path d="M270 315 q-62 -22 -70 -62 m-2 14 l2 -14 l12 8" stroke="{DEEP}" stroke-width="4" fill="none"/>'
         + f'<path d="M200 150 q15 -45 62 -62 m-10 -4 l10 4 l-4 12" stroke="{DEEP}" stroke-width="4" fill="none"/>'
         )

def src(label, url):
    return f'<li><a href="{url}" target="_blank" rel="noopener">{label}</a></li>'

CARDS = [
 (a1, '1', 'เศษพืชในไร่ ถูกเผาทุกปี',
  'ตอซัง ใบอ้อย ฟาง เหลือหลังเก็บเกี่ยวจำนวนมาก ส่วนหนึ่งถูกเผา',
  ['เศษใบและยอดอ้อยในไร่ ประมาณ 20 ล้านตันต่อปี และถูกเผาราว 12 ล้านตัน (ค่าเฉลี่ยช่วงปี 2545/46–2554/55)',
   'ฟางข้าวและตอซังเป็นสัดส่วนราว 70% ของเศษพืชที่ถูกเผาในที่โล่งของไทย',
   'ชานอ้อยที่ออกจากโรงงานส่วนใหญ่ถูกใช้เป็นเชื้อเพลิงผลิตไฟฟ้าอยู่แล้ว (ราว 30.7 ล้านตันในปี 2559) เราจึงมุ่งไปที่ ฟางและใบอ้อยในไร่ ที่ยังถูกเผาทิ้ง'],
  [('เศษอ้อยในไร่ (มหาวิทยาลัยทักษิณ)', 'https://ebook.tsu.ac.th/store/book/research/full2013_e/full2013_e/assets/basic-html/page13.html'),
   ('ฟางข้าวและผลกระทบสุขภาพ (TCI-Thaijo)', 'https://so05.tci-thaijo.org/index.php/teej/article/download/256260/174186/958025'),
   ('ชานอ้อยและไฟฟ้า, Sugar Tech 2018', 'https://link.springer.com/10.1007/s12355-018-0599-x')]),
 (a2, '2', 'ควันเผา คือฝุ่นที่เข้าถึงปอด',
  'ฝุ่น PM2.5 จากการเผาเกี่ยวข้องกับโรคทางเดินหายใจ',
  ['งานประเมินระดับจังหวัด พบว่าการเผาเศษพืช 5 ชนิด สร้างความเสียหายด้านสุขภาพและสิ่งแวดล้อมราว 5.24 แสนล้านบาท ขณะที่ทางเลือกอื่น เช่น อาหารสัตว์ ปุ๋ย ผลิตไฟฟ้า ให้ผลสุทธิเป็นบวก',
   'ถ้าเผาฟางข้าวทั้งหมด ผลกระทบต่อสุขภาพเพิ่ม 81.1% เมื่อเทียบกับกรณีปกติ',
   'ปอดของคนในพื้นที่เสี่ยงจึงควรได้ตรวจสมรรถภาพปอดสม่ำเสมอ ซึ่งเป็นหน้าที่ของเครื่องนี้'],
  [('ความเสียหายจากการเผา (ม.มหิดล)', 'https://repository.li.mahidol.ac.th/handle/123456789/98397'),
   ('ฟางข้าว: ผลกระทบสุขภาพ (TCI-Thaijo)', 'https://so05.tci-thaijo.org/index.php/teej/article/download/256260/174186/958025')]),
 (a3, '3', 'เปลี่ยนเศษพืชเป็นเยื่อ ขึ้นรูปเป็นที่เป่า',
  'เยื่อฟางและชานอ้อยขึ้นรูป เป็นวัสดุที่ย่อยสลายได้',
  ['ถาดเยื่อฟางข้าวที่ใส่ฟางได้ถึง 80% มีค่าความแข็งแรงดึงสูงกว่าโฟม EPS และสูญเสียมวลราว 20% ใน 4 สัปดาห์เมื่อฝังในดิน (Bangor University)',
   'บรรจุภัณฑ์จากฟางข้าวและชานอ้อย ใช้แป้งมันเป็นตัวประสาน และเคลือบไคโตซาน ลดการดูดน้ำได้มาก (วารสารวิทยาศาสตร์ มหาวิทยาลัยบูรพา)',
   'เป็นเทคโนโลยีเดียวกับกล่องข้าวและถาดเยื่อที่ใช้กันอยู่ เหมาะกับการผลิตจำนวนมากราคาถูก'],
  [('Bangor University: ถาดเยื่อฟาง', 'https://research.bangor.ac.uk/portal/en/researchoutputs/feasibility-of-using-straw-in-a-strong-thin-pulp-moulded-packaging-material(d81fbefc-e0b5-45b1-9006-a1bcc9c9c66d)/export.html'),
   ('บรรจุภัณฑ์เยื่อฟางและชานอ้อยเคลือบไคโตซาน', 'https://li05.tci-thaijo.org/index.php/buuscij/article/view/1311')]),
 (a4, '4', 'เปลี่ยนเฉพาะส่วนที่สัมผัสปาก',
  'ท่อวัดที่แม่นยำคงเดิม ที่เป่าเปลี่ยนทุกคน',
  ['ท่อ venturi (Ø28 มม. / คอคอด Ø23 มม.) ที่ต้องแม่นยำ ยังเป็นชิ้นพิมพ์ ล้างและใช้ซ้ำได้',
   'ที่เป่าสวมเข้าช่อง Ø30.4 มม. ถอดเปลี่ยนได้ เครื่องนับ 20 ครั้งหรือ 7 วัน แล้วเตือนให้เปลี่ยน',
   'แนวคิดท่อลมใช้แล้วทิ้งจากกระดาษ/วัสดุย่อยสลายได้ มีในสิทธิบัตรสไปโรมิเตอร์ (US 5,980,466 และ 6,176,833) และโครงงานนักศึกษา University of Wisconsin–Madison ใช้ที่เป่ากระดาษแข็งกับตัวเครื่องพลาสติกใช้ซ้ำ หลังสอบเทียบผ่านเกณฑ์ปริมาตร ATS 28 จาก 30 ครั้ง',
   'ต้นแบบตอนนี้พิมพ์ที่เป่าจาก PETG เพื่อตรวจขนาดและการสวม ก่อนเปลี่ยนเป็นเยื่อพืช'],
  [('สิทธิบัตร US 6,176,833 Biodegradable air tube', 'https://patents.google.com/patent/US6176833'),
   ('สิทธิบัตร US 5,980,466', 'https://www.google.com.au/patents/US5980466'),
   ('โปสเตอร์ UW–Madison', 'https://bmedesign.engr.wisc.edu/public/projects/f09/spirometer/file/view/408e0168-4392-4fac-9b9c-8246935e60cf/Final_Poster_12_3.pdf')]),
 (a5, '5', 'เลือกวัสดุอย่างไร',
  'ต้นแบบ PETG → เยื่อพืช → กระดาษม้วนเป็นตัวเลือกสำรอง',
  ['ระยะต้นแบบ: PETG พิมพ์ 3 มิติ ได้ขนาดตรงเร็ว ใช้ตรวจการสวมและความต้านทานลม',
   'ระยะผลิตจริง: เยื่อฟางข้าว/ใบอ้อยขึ้นรูป ย่อยสลายได้ ใช้วัตถุดิบที่ถูกเผาทิ้ง',
   'ตัวเลือกสำรอง: ที่เป่ากระดาษม้วนมาตรฐานของ spirometer ซึ่งมีขายทั่วไป',
   'ชานอ้อยจากโรงงานมักถูกใช้เป็นเชื้อเพลิงอยู่แล้ว จึงเลือกเศษที่ยังถูกเผาในไร่เป็นหลัก'],
  [('เยื่อชานอ้อยและความแข็งแรง (Molecules 2025)', 'https://mdpi-res.com/d_attachment/molecules/molecules-30-01583/article_deploy/molecules-30-01583.pdf')]),
 (a6, '6', 'เศษพืชมีมูลค่า ปอดได้ตรวจเร็วขึ้น',
  'วงจรหมุนเวียนระหว่างชุมชนเกษตรกับสุขภาพ',
  ['ชุมชนปลูกข้าว/อ้อยมีรายได้จากเศษที่เคยเผา ฝุ่นจากการเผาลดลง',
   'โรงเรียนและ รพ.สต. ได้เครื่องตรวจปอดราคาย่อมเยา ใช้วัสดุท้องถิ่น',
   'เป็นต้นแบบเศรษฐกิจหมุนเวียนที่เชื่อมสุขภาพกับสิ่งแวดล้อม'],
  []),
]

import os, base64
IMGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'story')
def photo(i, art):
    f = os.path.join(IMGDIR, f's{i+1}.jpg')
    if os.path.exists(f):
        return '<img alt="" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block" src="data:image/jpeg;base64,' + base64.b64encode(open(f,'rb').read()).decode() + '">'
    return art
cards, tpls = [], []
for i, (art, k, title, short, pts, srcs) in enumerate(CARDS):
    art = photo(i, art)
    cards.append(f'<article class="sc" role="button" tabindex="0" data-i="{i}"><div class="sart">{art}</div><div class="sbody"><span class="sk">{k}</span><h3>{title}</h3><p>{short}</p><span class="more">ดูรายละเอียด +</span></div></article>')
    li = ''.join(f'<li>{p}</li>' for p in pts)
    sl = ('<h4>แหล่งอ้างอิง</h4><ul class="slinks">' + ''.join(src(*s) for s in srcs) + '</ul>') if srcs else ''
    tpls.append(f'<template id="sd{i}"><h3>{k} · {title}</h3><ul class="spts">{li}</ul>{sl}</template>')

SECTION = ('<section id="story">\n'
 '  <div class="sec-h"><span class="eyebrow">เรื่องราวของวัสดุ</span><h2>จากเศษเหลือทิ้งในไร่ สู่ที่เป่าที่ย่อยสลายได้</h2>\n'
 '  <p>เผาเศษพืช → ฝุ่น PM2.5 → ปอดเสีย → ต้องตรวจปอด เราจึงเปลี่ยนเศษพืชนั้นให้เป็นส่วนที่ใช้ตรวจ แตะการ์ดเพื่อดูรายละเอียด</p></div>\n'
 '  <div class="feat sgrid">' + '\n'.join(cards) + '</div>\n'
 + '\n'.join(tpls) + '\n'
 '  <dialog id="sdlg"><button class="sx" type="button" aria-label="ปิด">×</button><div class="sbig" id="sbig"></div><div class="sdet" id="sdet"></div>'
 '<div class="snav"><button type="button" id="sprev">← ก่อนหน้า</button><button type="button" id="snext">ถัดไป →</button></div></dialog>\n'
 '</section>\n')

CSS = '''/*story*/
.sgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}
.feat article.sc,.sc{padding:0;cursor:pointer;overflow:hidden;display:flex;flex-direction:column;transition:transform .2s,box-shadow .2s}
.sc:hover,.sc:focus-visible{transform:translateY(-3px);box-shadow:var(--shadow)}.sc:focus-visible{outline:3px solid var(--blue)}
.sart{aspect-ratio:16/10;background:var(--blue-soft)}.sart svg{display:block;width:100%;height:100%}
.sbody{padding:16px 18px 18px}.sbody h3{margin:4px 0 6px}.sbody p{color:var(--mute);font-size:15px}
.sk{font:800 13px var(--disp);color:var(--blue)}.more{display:inline-block;margin-top:10px;font-weight:700;color:var(--blue);font-size:14px}
#sdlg{border:0;border-radius:20px;padding:0;max-width:min(880px,94vw);width:100%;background:var(--panel);color:var(--ink);box-shadow:0 30px 80px -20px rgba(0,0,0,.6)}
#sdlg::backdrop{background:rgba(5,15,28,.72)}
#sdlg .sbig svg{display:block;width:100%;height:auto;max-height:52vh;background:var(--blue-soft)}
.sdet{padding:18px 24px 8px;max-height:36vh;overflow:auto}.sdet h3{font-size:20px;margin-bottom:10px}
.spts{margin:0 0 12px;padding-left:20px}.spts li{margin:6px 0;color:var(--ink)}
.sdet h4{margin:10px 0 4px;font-size:14px;color:var(--mute)}.slinks{margin:0;padding-left:20px;font-size:14px}
.sx{position:absolute;right:10px;top:10px;width:40px;height:40px;border-radius:50%;border:0;background:rgba(0,0,0,.55);color:#fff;font-size:26px;line-height:1;cursor:pointer}
.snav{display:flex;justify-content:space-between;padding:8px 24px 18px}.snav button{border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:999px;padding:8px 16px;cursor:pointer;font:inherit}
'''
JS = '''/*story*/
(()=>{const d=document.getElementById("sdlg");if(!d)return;const cards=[...document.querySelectorAll(".sc")];let cur=0;
function show(i){cur=(i+cards.length)%cards.length;document.getElementById("sbig").innerHTML=cards[cur].querySelector(".sart").innerHTML;
const t=document.getElementById("sd"+cur);document.getElementById("sdet").innerHTML="";document.getElementById("sdet").appendChild(t.content.cloneNode(true));}
cards.forEach((c,i)=>{c.onclick=()=>{show(i);d.showModal();};c.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();c.onclick();}};});
d.querySelector(".sx").onclick=()=>d.close();document.getElementById("sprev").onclick=()=>show(cur-1);document.getElementById("snext").onclick=()=>show(cur+1);
d.addEventListener("click",e=>{if(e.target===d)d.close();});})();
'''

s = P.read_text(encoding='utf-8')
s = re.sub(r'<section id="story">.*?</section>\n', lambda m: SECTION, s, count=1, flags=re.S)
s = re.sub(r'/\*story\*/.*?(?=</style>)', '', s, count=1, flags=re.S) if '/*story*/' in s.split('</style>')[0] else s
s = s.replace('</style>', CSS + '</style>', 1)
s = re.sub(r'/\*story\*/\n\(\(\)=>\{.*?\}\)\(\);\n', '', s, flags=re.S)
s = s.replace('</script>', JS + '</script>', 1) if s.count('</script>') == 1 else s[:s.rfind('</script>')] + JS + s[s.rfind('</script>'):]
P.write_text(s, encoding='utf-8')
print('ok', len(s))
