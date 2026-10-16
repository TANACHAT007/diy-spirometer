# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# Borrow the HK-Green-15 site's friendly look: pastel emoji tiles, spring hover, floating hero + chips, stat strip, scroll reveal.
import re, pathlib
P = pathlib.Path(__file__).with_name('product_page.src.html')
s = P.read_text(encoding='utf-8')

# font
s = s.replace('family=Sora:wght@500;700;800&family=Noto+Sans+Thai:wght@400;500;700&display=swap', 'family=Sora:wght@500;700;800&family=Anuphan:wght@400;500;600;700&family=Noto+Sans+Thai:wght@400;500;700&display=swap') if 'Anuphan' not in s else s
s = s.replace('--body:"Noto Sans Thai","Sora",system-ui,sans-serif;', '--body:"Anuphan","Noto Sans Thai","Sora",system-ui,sans-serif;') if '--body:"Anuphan"' not in s else s

# icons on the first feature grid
ICONS = [('#fff3d6','🧽'),('#e3f6ff','🔧'),('#fff0e0','⚡'),('#e4fbef','🎯'),('#efe8ff','📡'),('#ffe6f2','🩺'),('#e3f6ff','🔊'),('#fff3d6','🌾'),('#e4fbef','🔋')]
a = s.index('<div class="feat">'); b = s.index('</section>', a)
blk = s[a:b]
if 'class="ic"' not in blk:
    it = iter(ICONS)
    blk = re.sub(r'<article><span class="k">', lambda m: '<article class="fc reveal"><div class="ic" style="background:%s">%s</div><span class="k">' % next(it), blk)
    s = s[:a] + blk + s[b:]

# stat strip after hero
STATS = ('<div class="stats reveal"><div><b>3</b><span>ค่าที่วัด · FVC FEV1 PEF</span></div><div><b>400 Hz</b><span>อ่านความดันต่าง</span></div>'
         '<div><b>10</b><span>ชิ้นพิมพ์ 3 มิติ</span></div><div><b>20 / 7</b><span>ครั้ง / วัน ต่อที่เป่า</span></div><div><b>≈ 3.1k ฿</b><span>ค่าวัสดุทั้งชุด (ประมาณ)</span></div></div>\n')
if 'class="stats' not in s:
    s = s.replace('</header>\n', '</header>\n' + STATS, 1)

# floating chips on hero stage
CH = ('<div class="stage"><img src="{{HERO}}" alt="เครื่อง DIY IoT Spirometer บนแท่นชาร์จ">'
      '<div class="fchip c1"><span>🫁</span><div>FVC · FEV1 · PEF<small>เป่าครั้งเดียวได้ครบ</small></div></div>'
      '<div class="fchip c2"><span>📡</span><div>BLE + Wi-Fi<small>ผลขึ้นเว็บทันที</small></div></div>'
      '<div class="fchip c3"><span>🌾</span><div>ที่เป่าจากเศษพืช<small>เปลี่ยนใหม่ทุกคน</small></div></div></div>')
s = re.sub(r'<div class="stage"><img src="\{\{HERO\}\}"[^>]*></div>', lambda m: CH, s, count=1) if 'fchip' not in s else s

CSS = '''/*hkstyle*/
:root{--spring:cubic-bezier(.34,1.56,.64,1)}
.fc{transition:transform .4s var(--spring),box-shadow .3s;border-radius:26px!important;box-shadow:var(--shadow)}
.fc:hover,.feat article.sc:hover{transform:translateY(-6px) rotate(-.4deg)}
.feat .ic{width:52px;height:52px;border-radius:17px;display:grid;place-items:center;font-size:26px;margin-bottom:12px}
.feat .fc .k{display:inline-block;font:700 12px var(--disp);background:var(--blue-soft);color:var(--blue);border-radius:99px;padding:3px 10px;margin-bottom:8px}
.feat article.sc{border-radius:26px;box-shadow:var(--shadow)}
.btn{border-radius:999px;transition:transform .35s var(--spring),box-shadow .3s;background:linear-gradient(135deg,var(--blue),#22c3a6);box-shadow:0 12px 26px -10px rgba(42,134,212,.55)}
.btn:hover{transform:translateY(-3px)}.btn:active{transform:translateY(1px) scale(.97)}
.btn.ghost{background:var(--panel);box-shadow:var(--shadow)}
.stage{position:relative;border-radius:34px}.stage>img{animation:fl 6s ease-in-out infinite}
@keyframes fl{50%{transform:translateY(-8px)}}
.fchip{position:absolute;display:flex;gap:10px;align-items:center;padding:9px 14px;border-radius:16px;background:var(--panel);box-shadow:var(--shadow);border:1px solid var(--line);font-weight:600;font-size:14px;line-height:1.25;animation:fl 5s ease-in-out infinite}
.fchip span{font-size:22px}.fchip small{display:block;color:var(--mute);font-weight:400;font-size:12px}
.fchip.c1{left:-14px;top:10%}.fchip.c2{right:-10px;top:42%;animation-delay:-1.6s}.fchip.c3{left:6%;bottom:6%;animation-delay:-3s}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;padding-block:4px 40px}
.stats div{background:var(--panel);border-radius:22px;padding:16px 18px;box-shadow:var(--shadow);border:1px solid var(--line)}
.stats b{display:block;font:800 26px var(--disp);color:var(--ink);font-variant-numeric:tabular-nums}.stats span{font-size:13px;color:var(--mute)}
nav b::before{content:"🫁";display:inline-grid;place-items:center;width:34px;height:34px;border-radius:12px;margin-right:9px;font-size:18px;background:linear-gradient(135deg,var(--blue),#22c3a6);animation:bob 3s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(-3px) rotate(-8deg)}}
nav a{padding:7px 12px;border-radius:999px;transition:background .2s}nav a:hover{background:var(--blue-soft)}
.reveal{opacity:0;transform:translateY(22px);transition:opacity .6s,transform .6s var(--spring)}.reveal.in{opacity:1;transform:none}
@media (max-width:820px){.fchip.c1{left:4px}.fchip.c2{right:4px}.fchip{font-size:12px;padding:7px 10px}}
@media (prefers-reduced-motion:reduce){.stage>img,.fchip,nav b::before{animation:none}.reveal{opacity:1;transform:none;transition:none}}
'''
JS = '''/*hkstyle*/
(()=>{const els=[...document.querySelectorAll(".reveal")];if(!("IntersectionObserver" in window)){els.forEach(e=>e.classList.add("in"));return;}
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target);}}),{threshold:.12});els.forEach(e=>io.observe(e));
setTimeout(()=>els.forEach(e=>e.classList.add("in")),2500);})();
'''
s = re.sub(r'/\*hkstyle\*/\n:root\{--spring.*?(?=</style>)', '', s, flags=re.S)
s = re.sub(r'/\*hkstyle\*/\n\(\(\)=>\{.*?\}\)\(\);\n', '', s, flags=re.S)
s = s.replace('</style>', CSS + '</style>', 1)
i = s.rfind('</script>'); s = s[:i] + JS + s[i:]
P.write_text(s, encoding='utf-8'); print('ok', s.count('class="ic"'), s.count('fchip'))
