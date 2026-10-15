# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# DIY IoT Spirometer (ndd-style pistol grip + charging dock) — Fusion model
# run: copy to ~/fusion-bridge/inbox/<ts>_model.py ; result ~/fusion-bridge/outbox/<ts>_model.json
# World: x = along the flow tube (mouth end x=0 → exit x=170), z up (tube axis z=0), y = across the body.
# Grip frame G(u, y, w): u along the slanted grip (down/back), w across it (0 = back line, 50 = front line).
import os, math
SK = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion-design', 'references')
exec(open(os.path.join(SK, 'fusion_lib.py'), encoding='utf-8').read())
exec(open(os.path.join(SK, 'fusion_parts.py'), encoding='utf-8').read())
exec(open(os.path.join(SK, 'fusion_fasteners.py'), encoding='utf-8').read())
exec(open(os.path.join(SK, 'fusion_wearable.py'), encoding='utf-8').read())     # cut_with, drill, round_*, place_cs, lipo
PROJECT = 'diy-spirometer'
PP = project_paths(PROJECT)
new_design(PROJECT, [('D_PIPE', 28, 'venturi pipe bore'), ('D_THROAT', 23, 'venturi throat'),
                     ('TUBE_OD', 34, 'flow tube OD')], prefix='sp_')

# ---------------------------------------------------------------- parameters (mm)
TUBE_L, TUBE_OD, D_PIPE, D_THR, D_SOCK = 170.0, 34.0, 28.0, 23.0, 30.4
X_TAP1, X_CONV0 = 54.0, 60.0
X_THR0 = X_CONV0 + (D_PIPE - D_THR) / 2 / math.tan(math.radians(10.5))
X_THR1 = X_THR0 + 11.5
X_TAP2 = (X_THR0 + X_THR1) / 2
X_DIV1 = X_THR1 + (D_PIPE - D_THR) / 2 / math.tan(math.radians(7.0))
SLV_X0, SLV_X1, SLV_OD = 25.0, 150.0, 48.0
BORE = TUBE_OD + 0.4                       # user fit rule: 0.4 total on printed mating parts
BODY_T, WALL = 30.0, 2.4
YI = BODY_T / 2 - WALL                     # inner wall face |y| = 12.6
TH = math.radians(34.0)
D_ = (math.sin(TH), 0.0, -math.cos(TH))    # grip axis (down the grip)
N_ = (math.cos(TH), 0.0, math.sin(TH))     # across the grip (toward the front)
Y_ = (0.0, 1.0, 0.0)
L0 = (30.0, -8.0)
GRIP_L, GRIP_W = 200.0, 50.0


def G(u, y, w):
    return (L0[0] + u * D_[0] + w * N_[0], y, L0[1] + u * D_[2] + w * N_[2])


def xz(u, w):
    g = G(u, 0, w)
    return (g[0], g[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def neg(v):
    return tuple(-c for c in v)


# ---------------------------------------------------------------- local helpers
def move_body(comp, body, origin, ex, ey, ez):
    col = adsk.core.ObjectCollection.create()
    col.add(body)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P3(*[v * MM for v in origin]), VEC(*ex), VEC(*ey), VEC(*ez))
    mi = comp.features.moveFeatures.createInput2(col)
    mi.defineAsFreeMove(m)
    comp.features.moveFeatures.add(mi)
    return body


def gbox(comp, name, u0, y0, w0, du, dy, dw, color='white'):
    """Box in the grip frame: u0..u0+du along the grip, y0..y0+dy, w0..w0+dw across it."""
    b = box(comp, name, 0, 0, 0, du, dy, dw, color)
    return move_body(comp, b, G(u0, y0, w0), D_, Y_, N_)


def gcyl(comp, name, u0, y, w, dia, L, color='white'):
    """Cylinder along the grip axis from u0 to u0+L."""
    b = cyl_z(comp, name, 0, 0, 0, dia, L, color)
    return move_body(comp, b, G(u0, y, w), Y_, N_, D_)


def seg3(comp, name, a, b, dia, color):
    v = tuple(b[i] - a[i] for i in range(3))
    L = math.sqrt(sum(c * c for c in v))
    ez = unit(v)
    t = (0, 0, 1) if abs(ez[2]) < 0.9 else (1, 0, 0)
    ex = unit(cross(t, ez))
    ey = cross(ez, ex)
    body = cyl_z(comp, name, 0, 0, 0, dia, L, color)
    return move_body(comp, body, a, ex, ey, ez)


def wire(comp, name, pts, dia=1.2, color='red'):
    for k in range(len(pts) - 1):
        seg3(comp, f'{name}_{k}', pts[k], pts[k + 1], dia, color)
    for k in range(1, len(pts) - 1):
        sphere(comp, f'{name}_bend_{k}', *pts[k], dia, color)


def keep_side(comp, body, side):
    """Cut away the other half (side -1 keeps y<0, +1 keeps y>0)."""
    t = box(comp, 'tmp_half', -100, 0 if side < 0 else -300, -400, 600, 300, 600, None)
    return cut_with(comp, body, t)


def yedge(body, x, z, tol=2.5):
    for e in body.edges:
        bb = e.boundingBox
        mn, mx = bb.minPoint, bb.maxPoint
        if (mx.y - mn.y) / MM < 0.8 * BODY_T:
            continue
        if abs((mn.x + mx.x) / 2 / MM - x) < tol and abs((mn.z + mx.z) / 2 / MM - z) < tol:
            return e
    return None


def fillet_one(comp, e, r, label):
    if e is None:
        print('fillet: edge not found', label)
        return
    col = adsk.core.ObjectCollection.create()
    col.add(e)
    _try_fillet(comp, col, r, label)


def yz_sketch(comp, x):
    """Sketch on a plane x = const (verified: yZ offset direction differs between docs)."""
    for off in (x, -x):
        pl = _plane(comp, comp.yZConstructionPlane, off)
        try:
            ox = pl.geometry.origin.x / MM
        except Exception:
            ox = off
        if abs(ox - x) < 0.01:
            return comp.sketches.add(pl)
    return comp.sketches.add(_plane(comp, comp.yZConstructionPlane, x))


def custom_color(key, rgb, base=('Plastic - Glossy (White)', 'Plastic - Matte (White)')):
    try:
        src = find_app(*base)
        a = design.appearances.itemByName(key) or design.appearances.addByCopy(src, key)
        done = 0
        for i in range(a.appearanceProperties.count):
            pr = a.appearanceProperties.item(i)
            if pr.objectType == adsk.core.ColorProperty.classType() and not pr.isReadOnly and \
                    any(s in pr.id.lower() for s in ('albedo', 'diffuse', 'color')):
                try:
                    pr.value = adsk.core.Color.create(*rgb, 255)
                    done += 1
                except Exception:
                    pass
        APP[key] = a
        print('colour', key, 'props set', done)
    except Exception as ex:
        print('colour failed', key, ex)


custom_color('lilac', (95, 170, 230))   # medical sky-blue (key name kept so the whole model re-colours)

# ---------------------------------------------------------------- body outline (side profile in x-z)
T_PT, A_PT, Q_PT = (150.0, -8.0), (150.0, -24.0), (130.0, -28.0)
B_U = 95.0
B_PT = xz(B_U, GRIP_W)
E_PT = xz(GRIP_L, GRIP_W)
LB_PT = xz(GRIP_L, 0)


def bump(u):                                   # 4 soft finger ridges on the front of the grip
    return 1.0 * (1 - math.cos(2 * math.pi * (u - 105) / 20.0)) if 105 <= u <= 185 else 0.0


SPL = [A_PT]
for t in (0.25, 0.5, 0.75):
    SPL.append(tuple((1 - t) ** 2 * A_PT[i] + 2 * t * (1 - t) * Q_PT[i] + t * t * B_PT[i] for i in range(2)))
u = B_U
while u < GRIP_L - 0.1:
    SPL.append(xz(u, GRIP_W + bump(u)))
    u += 2.5
SPL.append(E_PT)


def body_prism(comp, name, color):
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = name + '_profile'
    sp = lambda q: sk.modelToSketchSpace(P3(q[0] * MM, 0, q[1] * MM))
    col = adsk.core.ObjectCollection.create()
    for q in SPL:
        col.add(sp(q))
    spl = sk.sketchCurves.sketchFittedSplines.add(col)
    ln = sk.sketchCurves.sketchLines
    l1 = ln.addByTwoPoints(spl.endSketchPoint, sp(LB_PT))
    l2 = ln.addByTwoPoints(l1.endSketchPoint, sp(L0))
    l3 = ln.addByTwoPoints(l2.endSketchPoint, sp(T_PT))
    ln.addByTwoPoints(l3.endSketchPoint, spl.startSketchPoint)
    prof = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda pr: pr.areaProperties().area)
    ei = comp.features.extrudeFeatures.createInput(prof, OP.NewBodyFeatureOperation)
    ei.setSymmetricExtent(V(f'{BODY_T} mm'), True)
    b = comp.features.extrudeFeatures.add(ei).bodies.item(0)
    b.name = name
    paint(b, color)
    return b


# ---------------------------------------------------------------- positions shared by housing + internals
SCREWS = [(122.0, -30.0), xz(160, 11), xz(186, 40), xz(84, 11)]         # M3 csk + insert, along +y
DISP_C = (97.0, -50.0)                                                   # GC9A01 round TFT (left side)
BTN_C, LED_C = (97.0, -78.0), (111.0, -78.0)
MB_X0, MB_X1, MB_HW, MB_Z1 = 49.0, 86.0, 6.0, -26.0                    # manifold block under the flow tube: x range, half width, bottom z
SENS_X0, SENS_Z0 = X_TAP2 - 17.0, -46.0                                  # carrier pcb 26 x 14; barbs at +9 / +17
XIAO_U1, XIAO_W0, XIAO_Y0 = 197.3, 16.1, -6.0                            # pcb u 176.3..197.3, y -6.0..-4.8
BAT_U0, BAT_W0, BAT_Y0 = 98.0, 8.0, YI - 6.1                             # 603450 against the right wall
CONTACTS = ((13.0, -6.0), (37.0, 6.0))                                    # (w, y) brass insert contacts: each wholly inside ONE half
CONTACT_W = tuple(c_[0] for c_ in CONTACTS)
MAG_GRIP = (25.0, 4.0)                                                   # (w, y) dock alignment magnet
MAG_TOP = [(x, s * 20.6) for x in (32.0, 143.0) for s in (-1, 1)]        # cover magnets 5 x 2
USB_Y, USB_W = XIAO_Y0 + 1.2 + 1.6, XIAO_W0 + 8.9                         # USB-C centre on the grip end


def pad(i, upper):                             # XIAO castellated pad i (0 = USB end) top-surface point
    return XIAO_U1 - (2.9 + 2.54 * i), (XIAO_W0 + 17.4 if upper else XIAO_W0 + 0.4)


# ---------------------------------------------------------------- housing halves
def housing_half(side):
    nm = 'left' if side < 0 else 'right'
    c = new_comp(f'Housing_{nm.capitalize()}')
    b = body_prism(c, f'print_housing_{nm}', 'lilac')
    fillet_one(c, yedge(b, *A_PT), 3, 'A')
    fillet_one(c, yedge(b, *E_PT), 8, 'E')
    fillet_one(c, yedge(b, *LB_PT), 8, 'LB')
    round_plane(c, b, 'y', BODY_T / 2, 7)
    round_plane(c, b, 'y', -BODY_T / 2, 7)
    keep_side(c, b, side)
    v0 = b.volume
    try:
        faces = adsk.core.ObjectCollection.create()
        for f in b.faces:
            bb = f.boundingBox
            if abs(bb.minPoint.y) < 1e-4 and abs(bb.maxPoint.y) < 1e-4:
                faces.add(f)
        si = c.features.shellFeatures.createInput(faces, False)
        si.insideThickness = V(f'{WALL} mm')
        c.features.shellFeatures.add(si)
        print(f'shell {nm}: {v0 * 1000:.0f} -> {b.volume * 1000:.0f} mm3 ({faces.count} open faces)')
    except Exception as ex:
        print('SHELL FAILED', nm, ex)
    # sleeve added AFTER the shell (shell of the merged body failed): solid half-cylinder, then bore + cover seat
    s = cyl_x(c, 'sleeve', SLV_X0, 0, 0, SLV_OD, SLV_X1 - SLV_X0, 'lilac')
    round_plane(c, s, 'x', SLV_X0, 3)
    round_plane(c, s, 'x', SLV_X1, 3)
    keep_side(c, s, side)
    join(c, b, s)
    drill(c, b, 'x', 0, 0, SLV_X0 - 5, SLV_X1 + 5, BORE)
    cut_with(c, b, box(c, 'tmp_top', SLV_X0 - 5, -40, 0, SLV_X1 - SLV_X0 + 10, 80, 40, None))
    y0 =-YI - 0.9 if side < 0 else 0.0
    yw = -YI - 0.3 if side < 0 else 0.0                  # helper: start of a rib that grows from the wall (left)
    # screw bosses (through the cavity, half each)
    for k, (x, z) in enumerate(SCREWS):
        join(c, b, cyl_y(c, f'boss{k}', x, y0, z, 8, YI + 0.9, 'lilac'))
    # slot for the flow-tube manifold block (it drops in / lifts out with the tube)
    cut_with(c, b, box(c, 'tmp_mslot', MB_X0 - 0.5, -MB_HW - 0.5, -28.0, MB_X1 - MB_X0 + 1.0, 2 * MB_HW + 1.0, 12.0, None))
    # sensor carrier rails + end stops (pcb z -46..-44.4, |y| <= 7)
    yr0 = 6.4 if side > 0 else -YI - 0.3
    yr = YI + 0.3 - 6.4
    for z0 in (SENS_Z0 - 1.6, SENS_Z0 + 1.8):
        join(c, b, box(c, 'rail', SENS_X0 + 1.75, yr0, z0, 15, yr, 1.6, 'lilac'))
    join(c, b, box(c, 'stop', SENS_X0 - 1.5, yr0, SENS_Z0 - 1.6, 1.5, yr, 5.0, 'lilac'))
    if side > 0:
        join(c, b, box(c, 'stop', SENS_X0 + 26, yr0, SENS_Z0 - 1.6, 1.5, yr, 5.0, 'lilac'))
    # cover magnets (5 x 2) in the sleeve seat
    for x, y in MAG_TOP:
        if y * side > 0:
            drill(c, b, 'z', x, y, -2.1, 0.5, 5.2)
    # grip end: bosses for the brass contact inserts + dock magnet, then USB-C port + counterbore
    for w, cy in CONTACTS:
        if cy * side < 0:
            continue
        t = gcyl(c, 'cboss', GRIP_L - 7.0, cy, w, 7.0, 4.7, 'lilac')
        join(c, b, t)
        cut_with(c, b, gcyl(c, 'tmp_pilot', GRIP_L - 5.0, cy, w, 4.0, 6, None))
    if side > 0:
        t = gcyl(c, 'mboss', GRIP_L - 7.0, MAG_GRIP[1], MAG_GRIP[0], 8.0, 4.7, 'lilac')
        keep_side(c, t, side)
        join(c, b, t)
        cut_with(c, b, gcyl(c, 'tmp_mag', GRIP_L - 3.2, MAG_GRIP[1], MAG_GRIP[0], 6.2, 4, None))
    cut_with(c, b, gbox(c, 'tmp_usb', 196.0, USB_Y - 2.0, USB_W - 4.9, 6, 4.0, 9.8, None))
    cut_with(c, b, gbox(c, 'tmp_usbcb', XIAO_U1 + 1.3, USB_Y - 3.75, USB_W - 6.5, 4, 7.5, 13, None))
    if side < 0:
        # round display: window 32.6 + inside counterbore 36.0 x 1.4; 3 clip blocks with lips over the pcb
        drill(c, b, 'y', DISP_C[0], DISP_C[1], -BODY_T / 2 - 1, -YI + 0.1, 32.6)
        drill(c, b, 'y', DISP_C[0], DISP_C[1], -YI - 1.4, -YI + 0.1, 36.0)
        for ang in (0, 180, 270):
            a = math.radians(ang)
            cx, cz = DISP_C[0] + 21.4 * math.cos(a), DISP_C[1] + 21.4 * math.sin(a)
            join(c, b, box(c, 'clip', cx - 2.5, -YI - 0.3, cz - 2.5, 5, YI - 9.0 + 0.3, 5, 'lilac'))
            lx, lz = DISP_C[0] + 17.6 * math.cos(a), DISP_C[1] + 17.6 * math.sin(a)
            join(c, b, box(c, 'lip', lx - 2.0, -10.0, lz - 2.0, 4.0, 1.2, 4.0, 'lilac'))
        # button (6x6 tact, stem out) + bracket, LED 3 mm
        drill(c, b, 'y', BTN_C[0], BTN_C[1], -BODY_T / 2 - 1, -YI + 0.1, 4.0)
        drill(c, b, 'y', LED_C[0], LED_C[1], -BODY_T / 2 - 1, -YI + 0.1, 3.0)
        bx, bz = BTN_C
        for zz in (bz - 7, bz + 5):
            join(c, b, box(c, 'btn_post', bx - 4, -YI - 0.3, zz, 8, YI - 5.2 + 0.3, 2, 'lilac'))
        join(c, b, box(c, 'btn_bar', bx - 4, -7.2, bz - 5, 8, 2.0, 10, 'lilac'))
        # LED retainer: 1.4 mm rib directly behind the LED flange (between the two legs), held by two wall posts
        lx, lz = LED_C
        for zz in (lz - 6, lz + 5):
            join(c, b, box(c, 'led_post', lx - 0.7, -YI - 0.3, zz, 1.4, 2.7 + 0.3, 1, 'lilac'))
        join(c, b, box(c, 'led_rib', lx - 0.7, -YI + 1.0, lz - 6, 1.4, 1.4, 12, 'lilac'))
        # XIAO: short rails at both pcb ends (pads in the middle stay free for soldering) + top stop
        for u0, du in ((XIAO_U1 - 2.0, 2.0), (XIAO_U1 - 21.4, 2.2)):      # 2nd pair overlaps the stop block (no edge-only contact)
            for lo_w, lip_w, web_w in ((XIAO_W0, XIAO_W0, XIAO_W0 - 1.6), (XIAO_W0 + 16.4, XIAO_W0 + 17.2, XIAO_W0 + 17.8)):
                join(c, b, gbox(c, 'xrail_lo', u0, yw, lo_w, du, XIAO_Y0 - yw, 1.4, 'lilac'))
                join(c, b, gbox(c, 'xrail_web', u0, yw, web_w, du, XIAO_Y0 + 2.8 - yw, 1.6, 'lilac'))
                lw0 = lip_w - 0.3 if lip_w == XIAO_W0 else lip_w
                join(c, b, gbox(c, 'xrail_lip', u0, XIAO_Y0 + 1.4, lw0, du, 1.4, 1.2, 'lilac'))
        join(c, b, gbox(c, 'xstop', XIAO_U1 - 23.0, yw, XIAO_W0, 2.0, XIAO_Y0 + 2.8 - yw, 17.8, 'lilac'))
    else:
        # battery cradle: side walls + lips over the pouch edges, end stops leave the leads free
        for w_side, w_lip in ((BAT_W0 - 1.6, BAT_W0 - 1.6), (BAT_W0 + 34, BAT_W0 + 33)):
            join(c, b, gbox(c, 'bat_side', BAT_U0 + 2, BAT_Y0 - 1.2, w_side, 46, YI + 0.3 - BAT_Y0 + 1.2, 1.6, 'lilac'))
            join(c, b, gbox(c, 'bat_lip', BAT_U0 + 2, BAT_Y0 - 1.2, w_lip, 46, 1.2, 2.6, 'lilac'))
        for uu in (BAT_U0 - 6.6, BAT_U0 + 50):
            for w0 in (BAT_W0 + 2, BAT_W0 + 24):
                join(c, b, gbox(c, 'bat_stop', uu, BAT_Y0, w0, 1.6, YI + 0.3 - BAT_Y0, 8, 'lilac'))
    return c, b


HL, hl = housing_half(-1)
HR, hr = housing_half(+1)

# ---------------------------------------------------------------- flow tube (white, lifts out for washing)
FT = new_comp('Flow_Tube')
# stop rings (OD 42) outside both sleeve ends: the tube can't slide when the cover is on; it still lifts straight up.
# mouth ring has a 45 deg underside (prints without support standing on the mouth end), exit ring is a flat 3 mm lip.
prof = [(0, 17), (21, 17), (25, 21), (25, 17), (SLV_X1, 17), (SLV_X1, 21), (SLV_X1 + 3, 21), (SLV_X1 + 3, 17),
        (TUBE_L, 17), (TUBE_L, 14), (X_DIV1, 14), (X_THR1, D_THR / 2), (X_THR0, D_THR / 2),
        (X_CONV0, 14), (20, 14), (20, D_SOCK / 2), (0, D_SOCK / 2)]
sk = FT.sketches.add(FT.xZConstructionPlane)
pts = [sk.modelToSketchSpace(P3(x * MM, 0, r * MM)) for x, r in prof]
for i in range(len(pts)):
    sk.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])
ax = sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(P3(0, 0, 0)),
                                                 sk.modelToSketchSpace(P3(TUBE_L * MM, 0, 0)))
ax.isConstruction = True
pr = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda q: q.areaProperties().area)
ri = FT.features.revolveFeatures.createInput(pr, ax, OP.NewBodyFeatureOperation)
ri.setAngleExtent(False, V('360 deg'))
tube = FT.features.revolveFeatures.add(ri).bodies.item(0)
tube.name = 'print_flow_tube'
paint(tube, 'white')
# manifold block: tap1 (x 54) is carried by an internal channel to the sensor's inlet barb (x = SENS_X0+9), tap2 straight down.
# Both end in 4 mm nipples directly above the SDP810 barbs, joined by two STRAIGHT 8 mm silicone stubs (no bends, no kinks).
mb = box(FT, 'mblock', MB_X0, -MB_HW, MB_Z1, MB_X1 - MB_X0, 2 * MB_HW, 14.0, 'white')
fillet_v(FT, mb, 3.0)
join(FT, tube, mb)
BX1, BX2 = SENS_X0 + 9.0, SENS_X0 + 17.0                 # sensor barb x positions (inlet, throat)
CH_Z = -21.0
for bx_ in (BX1, BX2):
    join(FT, tube, cyl_z(FT, 'nipple', bx_, 0, MB_Z1 - 5.0, 4.0, 5.2, 'white'))
drill(FT, tube, 'z', X_TAP1, 0, CH_Z - 1.2, -12.0, 2.0)                  # tap 1 vertical, from the lumen
drill(FT, tube, 'x', 0, CH_Z, X_TAP1 - 1.0, BX1 + 1.2, 2.4)             # horizontal channel to the inlet barb
drill(FT, tube, 'z', BX1, 0, MB_Z1 - 6.0, CH_Z + 1.2, 2.0)              # down through the nipple
drill(FT, tube, 'z', BX2, 0, MB_Z1 - 6.0, -12.0, 2.0)                   # tap 2 straight down through the nipple
round_plane(FT, tube, 'x', 0, 1.0)
round_plane(FT, tube, 'x', TUBE_L, 1.0)
print(f'venturi: pipe {D_PIPE} throat {D_THR} conv {X_CONV0}-{X_THR0:.1f} throat -{X_THR1:.1f} div -{X_DIV1:.1f} '
      f'taps {X_TAP1} / {X_TAP2:.2f}')

# ---------------------------------------------------------------- top cover (magnetic, finger knob like the ndd)
TC = new_comp('Top_Cover')
cv = cyl_x(TC, 'print_top_cover', SLV_X0, 0, 0, SLV_OD, SLV_X1 - SLV_X0, 'lilac')
round_plane(TC, cv, 'x', SLV_X0, 3)
round_plane(TC, cv, 'x', SLV_X1, 3)
kn = cyl_y(TC, 'knob', 45, -27, 14, 16, 54, 'lilac')
round_plane(TC, kn, 'y', -27, 4)
round_plane(TC, kn, 'y', 27, 4)
join(TC, cv, kn)
drill(TC, cv, 'x', 0, 0, SLV_X0 - 5, SLV_X1 + 5, BORE)
cut_with(TC, cv, box(TC, 'tmp_low', SLV_X0 - 5, -40, -40, SLV_X1 - SLV_X0 + 10, 80, 40, None))
for x, y in MAG_TOP:
    drill(TC, cv, 'z', x, y, -0.5, 2.1, 5.2)

MG = new_comp('Magnets_5x2')
for i, (x, y) in enumerate(MAG_TOP):
    cyl_z(MG, f'magnet_low_{i}', x, y, -2.0, 5.0, 2.0, 'steel')
    cyl_z(MG, f'magnet_up_{i}', x, y, 0.0, 5.0, 2.0, 'steel')

# ---------------------------------------------------------------- mouthpiece (personal, washable)
MP = new_comp('Mouthpiece')


def loft2(comp, name, x1, r1, x2, ra, rb, color):
    s1 = yz_sketch(comp, x1)
    s1.sketchCurves.sketchCircles.addByCenterRadius(s1.modelToSketchSpace(P3(x1 * MM, 0, 0)), r1 * MM)
    s2 = yz_sketch(comp, x2)
    c0 = s2.modelToSketchSpace(P3(x2 * MM, 0, 0))
    s2.sketchCurves.sketchEllipses.add(c0, s2.modelToSketchSpace(P3(x2 * MM, ra * MM, 0)),
                                       s2.modelToSketchSpace(P3(x2 * MM, 0, rb * MM)))
    li = comp.features.loftFeatures.createInput(OP.NewBodyFeatureOperation)
    li.loftSections.add(s1.profiles.item(0))
    li.loftSections.add(s2.profiles.item(0))
    b = comp.features.loftFeatures.add(li).bodies.item(0)
    b.name = name
    paint(b, color)
    return b


try:
    mp = cyl_x(MP, 'print_mouthpiece', 0, 0, 0, D_SOCK - 0.4, 20, 'white')
    join(MP, mp, loft2(MP, 'mp_loft', 0.5, (D_SOCK - 0.4) / 2, -30, 17, 11, 'white'))
    cut_with(MP, mp, cyl_x(MP, 'tmp_in', -0.5, 0, 0, 26, 21, None))
    cut_with(MP, mp, loft2(MP, 'tmp_in2', 0.5, 13, -31, 15, 9, None))
except Exception as ex:
    print('MOUTHPIECE FAILED', ex)


# ---------------------------------------------------------------- electronics (real-looking modules)
def xiao_esp32s3(name, code='E1'):
    """Seeed XIAO ESP32S3 21 x 17.8: USB-C at local x=0, shield can, BOOT/RESET, U.FL, castellations, BAT pads."""
    c = new_comp(name)
    box(c, f'{code}_xiao_pcb', 0, 0, 0, 21, 17.8, 1.2, 'blue')
    for i in range(7):
        x = 2.9 + 2.54 * i
        for y0 in (0, 17.0):
            box(c, f'{code}_pad', x - 0.7, y0, 0, 1.4, 0.8, 1.21, 'brass')
    box(c, f'{code}_usbc', -1.3, 4.43, 1.2, 7.35, 8.94, 3.2, 'steel')
    box(c, f'{code}_usbc_mouth', -1.35, 5.2, 1.8, 0.9, 7.4, 2.0, 'black')
    box(c, f'{code}_shield_can_ESP32S3', 7.5, 1.8, 1.2, 11.0, 14.2, 2.3, 'steel')
    text_z(c, f'{code}_label', 'ESP32-S3', 13.0, 8.9, 3.5, 1.1, 'black')
    for y0, n in ((1.0, 'BOOT'), (14.3, 'RESET')):
        box(c, f'{code}_btn_{n}', 1.0, y0, 1.2, 3.0, 2.5, 0.8, 'steel')
    cyl_z(c, f'{code}_ufl', 19.9, 15.9, 1.2, 2.0, 1.2, 'brass')
    box(c, f'{code}_bat_pads', 15.5, 6.5, -0.05, 3.0, 4.8, 0.05, 'brass')
    return c


def sdp810(name, code='E2'):
    """Sensirion SDP810-500Pa on a 26 x 14 carrier: grey manifold body, 2 barbs 8 mm apart, 4-pin JST-GH."""
    c = new_comp(name)
    box(c, f'{code}_carrier_pcb', 0, 0, 0, 26, 14, 1.6, 'pcb')
    box(c, f'{code}_sdp810_body', 2, 1, 1.6, 22, 12, 6.0, 'grey')
    text_z(c, f'{code}_label', 'SDP810', 13, 3.5, 7.6, 1.4, 'black')
    for x in (9.0, 17.0):
        cyl_z(c, f'{code}_barb', x, 7, 7.6, 4.0, 5.8, 'grey')
        cyl_z(c, f'{code}_barb_ring', x, 7, 10.0, 4.8, 1.0, 'grey')
    box(c, f'{code}_jst_gh_4p', 0.6, 3.5, 1.6, 1.2, 7, 4.2, 'white')
    return c


def gc9a01(name, code='E3'):
    """1.28" round TFT GC9A01 240x240: glass Ø35.6 (face at local z=0), round pcb Ø37, 7-pin header tab."""
    c = new_comp(name)
    cyl_z(c, f'{code}_glass', 0, 0, 0, 35.6, 2.2, 'black')
    cyl_z(c, f'{code}_active_area', 0, 0, -0.02, 32.4, 0.02, 'blue')
    cyl_z(c, f'{code}_pcb', 0, 0, 2.2, 37.0, 1.6, 'blue')
    box(c, f'{code}_header_7p', -8.9, -17.5, 3.8, 17.8, 2.5, 2.5, 'black')
    return c


xi = xiao_esp32s3('E1_XIAO_ESP32S3')
place_cs(xi, G(XIAO_U1, XIAO_Y0, XIAO_W0), neg(D_), N_, (0, 1, 0))
sd = sdp810('E2_SDP810_500Pa')
place_cs(sd, (SENS_X0, -7.0, SENS_Z0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
tf = gc9a01('E3_GC9A01_Round_TFT')
place_cs(tf, (DISP_C[0], -YI - 1.4, DISP_C[1]), (1, 0, 0), (0, 0, -1), (0, 1, 0))
bat = lipo_pouch('E4_LiPo_603450', t=6.0, w=34.0, l=50.0, label='3.7V 1000mAh', model='603450', code='E4')
place_cs(bat, G(BAT_U0 + 50, BAT_Y0, BAT_W0), neg(D_), N_, (0, 1, 0))      # seal + PCM toward the top of the grip

BT = new_comp('E5_Button_6x6')
tact_6x6(BT, 'E5_tact', 0, 0, 0, h=7.0)
place_cs(BT, (BTN_C[0], -8.8, BTN_C[1]), (1, 0, 0), (0, 0, 1), (0, -1, 0))
LD = new_comp('E6_LED_3mm')
cyl_y(LD, 'E6_led_body', LED_C[0], -BODY_T / 2 - 1.4, LED_C[1], 3.0, 4.8, 'green')
cyl_y(LD, 'E6_led_flange', LED_C[0], -YI, LED_C[1], 3.8, 1.0, 'green')
for dx in (-1.27, 1.27):
    cyl_y(LD, 'E6_led_leg', LED_C[0] + dx, -YI + 1.0, LED_C[1], 0.5, 6, 'steel')

CC = new_comp('Charge_Contacts')
for w, cy in CONTACTS:
    gcyl(CC, 'brass_insert_M3_contact', GRIP_L - 4.0, cy, w, 4.0, 4.0, 'brass')
gcyl(CC, 'magnet_6x3_grip', GRIP_L - 3.0, MAG_GRIP[1], MAG_GRIP[0], 6.0, 3.0, 'steel')

# pneumatic: two straight silicone 3x5 stubs, nipple (under the manifold block) -> SDP810 barb
PN = new_comp('Silicone_Tube_3x5')
bx1, bx2 = SENS_X0 + 9.0, SENS_X0 + 17.0
zb = SENS_Z0 + 1.6 + 6.0 + 5.8                              # barb tip
for k_, bx_ in enumerate((bx1, bx2)):
    st_ = cyl_z(PN, f'sil_stub_{k_}', bx_, 0, zb - 3.0, 5.0, (MB_Z1 - 5.0 + 3.0) - (zb - 3.0), 'clear')
    cut_with(PN, st_, cyl_z(PN, 'tmp_bore', bx_, 0, zb - 3.5, 4.0, 20.0, None))      # barb / nipple OD 4 inside

# main wires (schematic): own y-level each, trunk via G(100, y, 25), end on a XIAO edge pad
WR = new_comp('Wires')


def to_pad(name, start, y, i, upper, color, dia=1.2, pre=()):
    uu, ww = pad(i, upper)
    wire(WR, name, [start, *pre, G(100, y, 25), G(170, y, ww), G(uu, y, ww), G(uu, XIAO_Y0 + 1.4, ww)], dia, color)


to_pad('w_battery', G(93.0, BAT_Y0 + 3, BAT_W0 + 13.6), 3.8, 6, True, 'red', pre=(G(93.0, 3.8, BAT_W0 + 13.6),))
to_pad('w_i2c_sdp810', (SENS_X0 + 0.6, 2.2, SENS_Z0 + 3.5), 2.2, 4, False, 'yellow', 1.6,
       pre=((SENS_X0 - 1.0, 2.2, SENS_Z0 + 1.0),))
to_pad('w_spi_tft', (DISP_C[0], -7.0, DISP_C[1] + 16.2), 0.4, 3, True, 'blue', 1.6,
       pre=((DISP_C[0], 0.4, DISP_C[1] + 16.2),))
to_pad('w_button', (BTN_C[0] + 4.6, -6.2, BTN_C[1]), -1.2, 1, False, 'green')
cu, cw = pad(1, True)
cy0 = CONTACTS[0][1]
wire(WR, 'w_charge_gnd', [G(GRIP_L - 7.0, cy0, CONTACT_W[0]), G(GRIP_L - 9.0, cy0, CONTACT_W[0]), G(cu, cy0, CONTACT_W[0]),
                          G(cu, cy0, cw), G(cu, XIAO_Y0 + 1.4, cw)], 1.2, 'black')

# ---------------------------------------------------------------- fasteners: halves (csk M3 into brass inserts)
for x, z in SCREWS:
    bolt_joint([(HL, hl), (HR, hr)], (x, -BODY_T / 2, z), (0, 1, 0), M=3, end='insert', head='csk', insert='M3x5x4.5')

# ---------------------------------------------------------------- charging dock
DK = new_comp('Dock')
slab = rbox(DK, 'print_dock', 50, -45, -198, 175, 90, 18, 6, 'white')
col_ = gbox(DK, 'collar', 180, -21, -6, 34, 42, 62, 'white')
round_all(DK, col_, 4)
wedge = rbox(DK, 'wedge', 140, -21, -190, 62, 42, 38, 4, 'white')
join(DK, slab, col_, wedge)
cut_with(DK, slab, gbox(DK, 'tmp_pocket', 170, -BODY_T / 2 - 0.2, -0.2, 30.4, BODY_T + 0.4, GRIP_W + 2.0 + 0.6, None))
for (w, cy), uend in zip(CONTACTS, (232.0, 247.0)):
    cut_with(DK, slab, gcyl(DK, 'tmp_pogo', GRIP_L, cy, w, 2.2, uend - GRIP_L, None))    # 2.0 pogo barrel + 0.2
cut_with(DK, slab, gcyl(DK, 'tmp_magd', GRIP_L + 0.4, MAG_GRIP[1], MAG_GRIP[0], 6.2, 3.2, None))
cut_with(DK, slab, box(DK, 'tmp_cav', 150, -20, -200, 68, 40, 12, None))
cut_with(DK, slab, box(DK, 'tmp_usb', 216, -4.9, -196.8, 12, 9.8, 4.0, None))
cut_with(DK, slab, box(DK, 'tmp_usbcb', 221, -6.5, -198.5, 6, 13, 7.5, None))
DB = new_comp('Dock_Bottom')
plate = box(DB, 'print_dock_bottom', 140, -31, -200.4, 85, 62, 2.4, 'white')
for x in (146.0, 220.5):
    for y in (-26.0, 26.0):
        bolt_joint([(DB, plate), (DK, slab)], (x, y, -200.4), (0, 0, 1), M=3, end='insert', head='csk')
FEET = new_comp('Rubber_Feet')
for x in (62, 213):
    for y in (-38, 38):
        cyl_z(FEET, 'foot_10x3', x, y, -201.0, 10, 3.0, 'black')
PG = new_comp('Pogo_Pins')
for w, cy in CONTACTS:
    gcyl(PG, 'pogo_plunger', GRIP_L, cy, w, 1.4, 2.0, 'brass')
    gcyl(PG, 'pogo_barrel', GRIP_L + 2.0, cy, w, 2.0, 10.0, 'brass')
gcyl(PG, 'magnet_6x3_dock', GRIP_L + 0.4, MAG_GRIP[1], MAG_GRIP[0], 6.0, 3.0, 'steel')
UC = new_comp('E7_USB_C_Breakout_Dock')
box(UC, 'E7_pcb', 204, -6, -198.0, 14, 12, 1.6, 'pcb')
box(UC, 'E7_usbc_receptacle', 212, -4.47, -196.4, 7.35, 8.94, 3.2, 'steel')

# ---------------------------------------------------------------- checks + views + exports
fasteners_finish(os.path.join(PP['bom'], 'fasteners_bom.csv'))
report()
views(PROJECT)
look(PROJECT + '_cu_inside.png', target=(110, 0, -80), eye=(110, -400, -60), extent=260,
     hide_comps=('Housing_Left', 'Top_Cover', 'Mouthpiece'))
look(PROJECT + '_cu_hero.png', target=(110, 0, -90), eye=(-180, -330, 120), extent=360)
look(PROJECT + '_cu_open.png', target=(90, 0, -20), eye=(60, -260, 220), extent=240, hide_comps=('Top_Cover',))
look(PROJECT + '_cu_dock.png', target=(170, 0, -175), eye=(330, -260, -60), extent=200,
     hide_comps=('Housing_Left', 'Housing_Right', 'Top_Cover', 'Flow_Tube', 'Mouthpiece'))
export_print_stl(PP['stl'])
export_step(os.path.join(PP['cad'], PROJECT + '_assembly.step'))
collect_renders(PROJECT, PP['renders'])
AUTO_SHOT = False
