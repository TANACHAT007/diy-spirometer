# Run in Fusion AFTER model.py: body count per print_* body, fastener + contact checks
import os
SK = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion-design', 'references')
for f in ('fusion_lib.py', 'fusion_fasteners.py'):
    exec(open(os.path.join(SK, f), encoding='utf-8').read())
design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct); root = design.rootComponent
for occ in root.allOccurrences:
    for b in occ.bRepBodies:
        if b.name.startswith('print_'):
            print('BODY', b.name, 'shells', b.shells.count, 'vol_cm3', round(b.volume, 1))
for fn in ('fastener_check', 'unfastened_contacts'):
    try:
        print('==', fn); r = globals()[fn](); print(r)
    except Exception as ex:
        print(fn, 'ERR', ex)
