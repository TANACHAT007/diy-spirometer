# Run in Fusion after model.py: half-cut views (right half hidden, so the left half + all electronics are visible)
import os
SK = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion-design', 'references')
exec(open(os.path.join(SK, 'fusion_lib.py'), encoding='utf-8').read())
app = adsk.core.Application.get(); design = adsk.fusion.Design.cast(app.activeProduct); root = design.rootComponent
P = 'diy-spirometer'
look(P + '_cut_side.png', target=(110, 0, -85), eye=(110, 420, -85), extent=240, hide_comps=('Housing_Right', 'Top_Cover'))
look(P + '_cut_iso.png', target=(110, 0, -70), eye=(-120, 330, 150), extent=320, hide_comps=('Housing_Right', 'Top_Cover'))
look(P + '_cut_grip.png', target=(140, 0, -120), eye=(300, 330, -40), extent=200, hide_comps=('Housing_Right', 'Top_Cover', 'Mouthpiece'))
