# Run in Fusion after model.py: dumps cylindrical features (holes/bosses) of every print_* body to 02_design/_brep_features.json (mm, world frame)
import adsk.core, adsk.fusion, json, os, math
app = adsk.core.Application.get()
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
OUT = os.path.join(os.path.expanduser('~'), 'fusion-projects', 'diy-spirometer', '02_design', '_brep_features.json')
res, seen = {}, {}
for occ in root.allOccurrences:
    for b in occ.bRepBodies:
        if not b.name.startswith('print_'):
            continue
        feats, keys = [], set()
        for f in b.faces:
            g = f.geometry
            if g.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
                continue
            o, a, r = g.origin, g.axis, g.radius
            p = f.pointOnFace
            ok, n = f.evaluator.getNormalAtPoint(p)
            rad = adsk.core.Vector3D.create(p.x - o.x, p.y - o.y, p.z - o.z)
            t = rad.dotProduct(a)
            rad.x -= a.x * t; rad.y -= a.y * t; rad.z -= a.z * t
            kind = 'hole' if n.dotProduct(rad) < 0 else 'boss'
            bb = f.boundingBox
            ext = [(bb.maxPoint.x - bb.minPoint.x), (bb.maxPoint.y - bb.minPoint.y), (bb.maxPoint.z - bb.minPoint.z)]
            ax = [abs(a.x), abs(a.y), abs(a.z)]
            ai = ax.index(max(ax))
            # centre of the face on the axis: foot of the bbox centre on the axis line
            c = [(bb.maxPoint.x + bb.minPoint.x) / 2, (bb.maxPoint.y + bb.minPoint.y) / 2, (bb.maxPoint.z + bb.minPoint.z) / 2]
            ctr = [o.x + a.x * ((c[0]-o.x)*a.x + (c[1]-o.y)*a.y + (c[2]-o.z)*a.z),
                   o.y + a.y * ((c[0]-o.x)*a.x + (c[1]-o.y)*a.y + (c[2]-o.z)*a.z),
                   o.z + a.z * ((c[0]-o.x)*a.x + (c[1]-o.y)*a.y + (c[2]-o.z)*a.z)]
            key = (kind, round(ctr[0]*10, 1), round(ctr[1]*10, 1), round(ctr[2]*10, 1), round(r*20, 1), ai)
            if key in keys:
                continue
            keys.add(key)
            feats.append({'kind': kind, 'center': [round(x * 10, 2) for x in ctr], 'axis': ['x', 'y', 'z'][ai],
                          'd': round(r * 20, 2), 'len': round(ext[ai] * 10, 2)})
        base = b.name[len('print_'):].replace(' ', '_').replace('(', '').replace(')', '')
        n = seen.get(base, 0) + 1
        seen[base] = n
        res[base + ('' if n == 1 else '_%d' % n)] = feats
json.dump(res, open(OUT, 'w'), indent=1)
print('parts', len(res), {k: len(v) for k, v in res.items()})
