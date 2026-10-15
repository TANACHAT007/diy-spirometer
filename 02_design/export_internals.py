# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# exports the non-printed parts (electronics, wires, tubing, magnets, pogo pins) as STL, assembled position, for the web viewer's "x-ray" mode
import os, re, json
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
out = os.path.join(os.path.expanduser('~'), 'fusion-projects', 'diy-spirometer', '10_manual', 'web', 'internals')
os.makedirs(out, exist_ok=True)
title = app.activeDocument.name
print('active document:', title)
if not any(o.component.name.startswith('E1_') for o in root.occurrences):
    raise RuntimeError('model not open: ' + title)
for f in os.listdir(out):
    if f.endswith('.stl'):
        os.remove(os.path.join(out, f))
KEEP = re.compile(r'^(E\d|Wires|Silicone|Charge_Contacts|Pogo|Magnets|Rubber)', re.I)
em = design.exportManager
done = []
for occ in root.occurrences:
    nm = occ.component.name
    if not KEEP.match(nm):
        continue
    if occ.bRepBodies.count == 0 and occ.childOccurrences.count == 0:
        continue
    fn = os.path.join(out, re.sub(r'[^A-Za-z0-9_]+', '_', nm) + '.stl')
    o = em.createSTLExportOptions(occ, fn)
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow
    em.execute(o)
    done.append((nm, os.path.getsize(fn) // 1024))
print('exported', len(done))
for d in done:
    print(' ', d)
