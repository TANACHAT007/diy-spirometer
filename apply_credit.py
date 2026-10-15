"""Stamps authorship credit into every deliverable so it travels with each download.
Edit NAME / TEAM / URL below, then run:  py apply_credit.py   (idempotent: re-running just refreshes the stamp)
Touches: LICENSE, LICENSE-DESIGN, CREDITS.md, README header, source-file headers, HTML meta+footer, STL header bytes, STEP header, render watermarks.
"""
import os, re, struct
NAME = 'Tanachat S.'
HANDLE = 'TANACHAT007'
TEAM = 'MEDTHAI'
URL = 'https://github.com/TANACHAT007/diy-spirometer'
YEAR = '2026'
LINE = f'DIY IoT Spirometer - designed by {NAME} ({HANDLE}) / {TEAM} - {YEAR} - {URL}'
TAG = 'CREDIT-STAMP'
ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)

def w(path, text):
    open(path, 'w', encoding='utf-8', newline='\n').write(text)

# ---- license + credits files
w(P('LICENSE'), f"""MIT License (source code: firmware, model.py, scripts, web pages)

Copyright (c) {YEAR} {NAME} ({HANDLE}) / {TEAM}

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

NOT A MEDICAL DEVICE: this project is an educational / screening prototype and has not been clinically validated.
""")
w(P('LICENSE-DESIGN'), f"""Creative Commons Attribution 4.0 International (CC BY 4.0)
Applies to: CAD models, STL/STEP files, renders, PCB files, BOM, manuals, posters, written documents.

Copyright (c) {YEAR} {NAME} ({HANDLE}) / {TEAM}

You are free to share and adapt this material for any purpose, even commercially, as long as you give appropriate credit:
  "{LINE}"
provide a link to the license, and indicate if changes were made.
Full text: https://creativecommons.org/licenses/by/4.0/legalcode
""")
w(P('CREDITS.md'), f"""# Credits

**Designed and built by {NAME}** (GitHub: [{HANDLE}](https://github.com/{HANDLE})) - team **{TEAM}**, {YEAR}.

If you reuse, remix or print this work, please keep this credit:

> {LINE}

- Code: MIT (`LICENSE`) - keep the copyright notice.
- Designs / documents / models: CC BY 4.0 (`LICENSE-DESIGN`) - attribution required.
- Prepared for International Youth Summit (IYS) 2026, sub-theme Health.

Third-party parts are credited to their makers (Sensirion SDP810, Seeed XIAO ESP32, GC9A01 modules); their names are used only to identify compatible parts.
""")

# ---- README header
rd = open(P('README.md'), encoding='utf-8').read()
rd = re.sub(r'<!-- ' + TAG + r' -->.*?<!-- /' + TAG + r' -->\n*', '', rd, flags=re.S)
rd = f"<!-- {TAG} -->\n> **Designed by {NAME} ({HANDLE}) / {TEAM}, {YEAR}** - please keep this credit when you use or share this work. See [CREDITS.md](CREDITS.md).\n<!-- /{TAG} -->\n\n" + rd
w(P('README.md'), rd)

# ---- source headers
def stamp_text(path, c):
    t = open(path, encoding='utf-8', errors='replace').read()
    t = re.sub(r'^' + re.escape(c) + r' ' + TAG + r'.*\n', '', t, flags=re.M)
    head = f'{c} {TAG}: (c) {YEAR} {NAME} ({HANDLE}) / {TEAM} - {URL} - MIT\n'
    if t.startswith('#!') or t.startswith('# -*-'):
        l1, rest = t.split('\n', 1); t = l1 + '\n' + head + rest
    else:
        t = head + t
    open(path, 'w', encoding='utf-8', newline='\n').write(t)

for root, _, files in os.walk(ROOT):
    if '.git' in root.split(os.sep):
        continue
    for f in files:
        p = os.path.join(root, f); ext = os.path.splitext(f)[1].lower()
        if f == 'apply_credit.py':
            continue
        if ext == '.ino':
            stamp_text(p, '//')
        elif ext == '.py':
            stamp_text(p, '#')
        elif ext == '.html':
            t = open(p, encoding='utf-8').read()
            t = re.sub(r'<!-- ' + TAG + r'.*?-->\n?', '', t)
            t = re.sub(r'<meta name="author"[^>]*>\n?', '', t)
            t = re.sub(r'<div class="credit-footer".*?</div>\n?', '', t, flags=re.S)
            meta = f'<!-- {TAG}: {LINE} -->\n<meta name="author" content="{NAME} ({HANDLE}) / {TEAM}">\n'
            foot = (f'<div class="credit-footer" style="text-align:center;font-size:12px;opacity:.7;padding:18px 0 28px">'
                    f'ออกแบบโดย {NAME} ({HANDLE}) · ทีม {TEAM} · {YEAR}</div>\n')
            if '<head>' in t:
                t = t.replace('<head>', '<head>\n' + meta, 1)
                t = t.replace('</body>', foot + '</body>', 1) if '</body>' in t else t + foot
            else:
                t = meta + t + foot
            open(p, 'w', encoding='utf-8', newline='\n').write(t)

# ---- STL: binary header carries the credit (80 bytes)
note = (f'{NAME} / {TEAM} {YEAR} CC-BY-4.0 {URL}').encode('ascii', 'replace')[:80].ljust(80, b' ')
for root, _, files in os.walk(P('04_print_stl')):
    for f in files:
        if f.lower().endswith('.stl'):
            p = os.path.join(root, f); b = open(p, 'rb').read()
            if b[:5] == b'solid' and b'facet' in b[:300]:
                continue                              # ASCII STL: leave untouched
            n = struct.unpack('<I', b[80:84])[0]
            if 84 + 50 * n == len(b):
                open(p, 'wb').write(note + b[80:])

# ---- STEP header
for root, _, files in os.walk(P('06_cad_export')):
    for f in files:
        if f.lower().endswith(('.step', '.stp')):
            p = os.path.join(root, f); t = open(p, encoding='utf-8', errors='replace').read()
            m = re.search(r"FILE_NAME\(([^;]*?)\);", t, re.S)
            if m:
                parts = m.group(1)
                new = re.sub(r"\('[^']*'\)", f"('{NAME} ({HANDLE})')", parts, count=1)
                new = re.sub(r"\('[^']*'\)(?=,\s*'[^']*',\s*'[^']*',)", f"('{TEAM} - {YEAR} - CC BY 4.0')", new, count=1)
                t = t.replace(m.group(1), new, 1)
                open(p, 'w', encoding='utf-8', newline='\n').write(t)

# ---- render watermarks (idempotent: originals are re-rendered by model.py, stamp is drawn on a copy of the bottom strip)
try:
    from PIL import Image, ImageDraw
    for root, _, files in os.walk(P('03_renders')):
        for f in files:
            if f.lower().endswith('.png') and not f.startswith('_'):
                p = os.path.join(root, f); im = Image.open(p).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
                txt = f'{TEAM} · {NAME} ({HANDLE}) · {YEAR}'
                x, y = 14, im.height - 26
                d.rectangle([x - 8, y - 6, x + 8 + 7 * len(txt), y + 18], fill=(255, 255, 255, 150))
                d.text((x, y), txt, fill=(30, 50, 80, 255))
                im.convert('RGB').save(p)
except Exception as e:
    print('watermark skipped:', e)
print('credit stamped:', LINE)
