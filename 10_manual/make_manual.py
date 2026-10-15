# Builds every manual of this project → 10_manual/<name>.pdf / .docx / .html  (rules: references/documentation.md)
# Images: Fusion job with fusion_docs.step_shots/part_thumbs → collect_doc(PREFIX, IMG); then annotate here.
import os, sys, json
sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion-design', 'references'))
from doc_lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG = os.path.join(HERE, 'img')
REN = os.path.join(ROOT, '03_renders')
PROJECT, TITLE = 'diy-spirometer', 'เครื่องวัดสมรรถภาพปอดพิมพ์ 3D (Spirometer)'
AUTHOR, ORG = '', ''
os.makedirs(IMG, exist_ok=True)


def hero():
    for f in sorted(os.listdir(REN)):
        if f.endswith('_iso.png'):
            return os.path.join(REN, f)


def steps_from_fusion(prefix):
    # [(png, title, {comp: [x, y]})] from fusion_docs.step_shots, trimmed to white with shifted anchors
    js = os.path.join(IMG, prefix + '_anchors.json')
    if not os.path.exists(js):
        return []
    out = []
    for fn, d in load_anchors(js).items():
        png, delta = trim(os.path.join(IMG, fn), os.path.join(IMG, 't_' + fn))
        out.append((png, d['title'], shift_anchors(d['new'], delta)))
    return out


# ---------------------------------------------------------------- assembly manual
a = Doc(TITLE, kind='assembly', project=PROJECT, author=AUTHOR, org=ORG, out_dir=HERE)
a.cover(hero())
a.toc()
a.h1('ความปลอดภัย')
a.safety('caution', 'ขอบชิ้นงานพิมพ์และแผ่นอะคริลิกอาจคม', 'อาจบาดมือ', ['สวมถุงมือขณะประกอบ'], ['M009'])
a.h1('ชิ้นส่วนและเครื่องมือ')
a.p('ซื้อตาม `09_bom/bom.md` · พิมพ์ตาม `04_print_stl/print_guide.md` · ตัดเลเซอร์ตาม `05_laser_dxf/`')
# a.parts([dict(id='A', name='...', qty=1, image=os.path.join(IMG, 'part_X.png'))])
# a.tools(['ประแจหกเหลี่ยม 2.5 มม.', 'ไขควง PH2'])
# a.screws([('M3', 8, 'socket', 12), ('M3', 0, 'nut', 12), ('M3', 5, 'insert', 10)])
a.h1('ขั้นตอนการประกอบ')
for i, (png, title, anc) in enumerate(steps_from_fusion('step'), 1):
    pts = [(x, y, str(j + 1)) for j, (x, y) in enumerate(anc.values())]
    img = annotate(png, os.path.join(IMG, f'a_step_{i:02d}.png'), callouts=pts, badge=i)
    a.step(title, img, parts=[(n, 1) for n in anc], actions=['...'])
a.h1('ทดสอบหลังประกอบ')
a.checklist(['ทุกสกรูขันแน่น', 'ไม่มีสายไฟเกะกะชิ้นส่วนที่เคลื่อนที่', 'เปิดเครื่องครั้งแรกโดยไม่มีโหลด'])
a.build('assembly_manual')

# ---------------------------------------------------------------- user / operating manual
u = Doc(TITLE, kind='operation', project=PROJECT, author=AUTHOR, org=ORG, out_dir=HERE)
u.cover(hero())
u.toc()
u.h1('รู้จักเครื่อง')
u.h1('ความปลอดภัย')
u.h1('วิธีใช้งาน')
# u.flow([dict(id='s', text='เปิดเครื่อง', type='start'), ..., dict(id='e', text='ปิดเครื่อง', type='end')])
u.h1('การดูแลรักษา')
u.h1('การแก้ไขปัญหา')
u.troubleshoot([('เครื่องไม่ทำงาน', 'ไม่มีไฟเข้า', 'ตรวจปลั๊ก/ฟิวส์')])
u.build('user_manual')

# ---------------------------------------------------------------- credits page source
src = os.path.join(ROOT, '01_reference', 'downloads', 'SOURCES.md')
if os.path.exists(src):
    print('remember: add credits from', src)
print('preview:', [pdf_preview(os.path.join(HERE, n + '.pdf'), os.path.join(HERE, '_preview', n)) and n for n in ('assembly_manual', 'user_manual')])
