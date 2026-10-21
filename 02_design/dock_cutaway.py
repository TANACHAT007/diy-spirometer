# Run in Fusion after model.py: dock views with the plate / cradle taken off (device parts hidden)
import os
SK = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion-design', 'references')
exec(open(os.path.join(SK, 'fusion_lib.py'), encoding='utf-8').read())
app = adsk.core.Application.get(); design = adsk.fusion.Design.cast(app.activeProduct); root = design.rootComponent
P = 'diy-spirometer'
KEEP = ('Dock', 'Dock_Bottom', 'Rubber_Feet', 'Pogo_Pins', 'Charge_Contacts')
dev = tuple(o.component.name for o in root.occurrences if o.component.name not in KEEP and 'M3x' not in o.component.name and 'M2' not in o.component.name and 'insert' not in o.component.name.lower() and 'magnet' not in o.component.name.lower())
print('hidden device comps:', len(dev))
look(P + '_dockcut_below.png', target=(152, 0, -192), eye=(60, -230, -420), extent=230, hide_comps=dev + ('Dock_Bottom',))
look(P + '_dockcut_top.png', target=(152, 0, -185), eye=(330, -260, -20), extent=230, hide_comps=dev)
look(P + '_dockcut_open.png', target=(152, 0, -185), eye=(330, -260, -20), extent=230, hide_comps=dev + ('Dock_Bottom',), hide_bodies=('print_dock_cradle',))
