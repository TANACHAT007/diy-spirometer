"""Generate voice/th|en/*.mp3 from VOICE in roles_train.js with Microsoft neural voices (edge-tts, no key; needs internet).
Usage: py gen_voice.py"""
import json, re, subprocess, asyncio, os
import edge_tts
src = open('roles_train.js', encoding='utf-8').read()
js = src[src.index('const VOICE='):src.index('let curAudio')] + '\nprocess.stdout.write(JSON.stringify(VOICE))'
V = json.loads(subprocess.check_output(['node', '-e', js.replace('const VOICE=', 'var VOICE=')]))
VO = {'th': 'th-TH-PremwadeeNeural', 'en': 'en-US-JennyNeural'}
async def main():
    for k, d in V.items():
        for l, voice in VO.items():
            os.makedirs(f'voice/{l}', exist_ok=True)
            for t in range(5):
                try: await edge_tts.Communicate(d[l], voice).save(f'voice/{l}/{k}.mp3'); break
                except Exception: await asyncio.sleep(2)
            else: print('FAILED', l, k)
asyncio.run(main()); print(len(V) * 2, 'files')
