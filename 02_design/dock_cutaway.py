# Run in Fusion after model.py: dock half-cut views (right half hidden, device parts hidden)
import os
SK = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion-design', 'references')
exec(open(os.path.join(SK, 'fusion_lib.py'), encoding='utf-8').read())
app = adsk.core.Application.get(); design = adsk.fusion.Design.cast(app.activeProduct); root = design.rootComponent
P = 'diy-spirometer'
KEEP = ('Dock_Left', 'Dock_Right', 'Dock_Inlays', 'Rubber_Feet', 'Pogo_Pins', 'Charge_Contacts', 'E7_USB_C_Breakout_Dock')
dev = tuple(o.component.name for o in root.occurrences if o.component.name not in KEEP and 'M3x' not in o.component.name and 'M2' not in o.component.name and 'insert' not in o.component.name.lower() and 'magnet' not in o.component.name.lower())
look(P + '_dockcut_open.png', target=(152, 0, -180), eye=(160, 380, -20), extent=230, hide_comps=dev + ('Dock_Right',))
look(P + '_dockcut_iso.png', target=(152, 0, -175), eye=(-60, 330, 150), extent=260, hide_comps=dev + ('Dock_Right',))
look(P + '_dockcut_full.png', target=(152, 0, -175), eye=(330, -260, -20), extent=230, hide_comps=dev)
