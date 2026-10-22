# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# Renders 4 clean transparent-background views of the real STL files with three.js (headless Edge) -> img/v_*.png
import base64, glob, json, os, re, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
b64 = lambda f: base64.b64encode(open(f, 'rb').read()).decode()
stl = {os.path.splitext(os.path.basename(f))[0]: b64(f) for f in sorted(glob.glob(os.path.join(H, '..', '..', '04_print_stl', '*.stl')))}
intr = {os.path.splitext(os.path.basename(f))[0]: b64(f) for f in sorted(glob.glob(os.path.join(H, 'internals', '*.stl')))}
hero = open(os.path.join(H, 'hero3d.html'), encoding='utf-8').read()
col = re.search(r'const COL=\{[^}]*\}', hero).group(0); icol = re.search(r'const ICOL=\{[^}]*\}', hero).group(0)
PAGE = '''<!doctype html><meta charset=utf-8><body style="margin:0;background:transparent">
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
<script>
const DATA=%s, INT=%s; %s; %s;
const W=1600,Hh=1000, cv=document.createElement('canvas'); cv.width=W; cv.height=Hh;
const ren=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:true,preserveDrawingBuffer:true}); ren.setSize(W,Hh,false); ren.setClearColor(0,0); ren.outputEncoding=THREE.sRGBEncoding;
const scene=new THREE.Scene(); const cam=new THREE.PerspectiveCamera(26,W/Hh,1,5000);
scene.add(new THREE.HemisphereLight(0xffffff,0x9db8d8,.5));
const k1=new THREE.DirectionalLight(0xffffff,.55); k1.position.set(300,500,400); scene.add(k1);
const k2=new THREE.DirectionalLight(0xbfe0ff,.3); k2.position.set(-400,200,-300); scene.add(k2);
const k3=new THREE.DirectionalLight(0xffffff,.15); k3.position.set(0,-300,300); scene.add(k3);
const root=new THREE.Group(); root.rotation.x=-Math.PI/2; const pivot=new THREE.Group(); pivot.add(root); scene.add(pivot);
const ld=new THREE.STLLoader(); const parts={}, inner=[];
const dec=s=>{const b=atob(s),u=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u.buffer};
for(const k in DATA){const g=ld.parse(dec(DATA[k]));g.computeVertexNormals();
  const tr=(k==='flow_tube'||k==='mouthpiece');
  const solid=new THREE.MeshStandardMaterial({color:COL[k]||0xffffff,roughness:.42,metalness:.02,transparent:tr,opacity:tr?.94:1});
  const ghost=new THREE.MeshPhysicalMaterial({color:0x8cc8ff,transparent:true,opacity:.16,depthWrite:false,roughness:.2,side:THREE.DoubleSide});
  const m=new THREE.Mesh(g,solid); root.add(m); parts[k]={m,solid,ghost}}
for(const k in INT){const g=ld.parse(dec(INT[k]));g.computeVertexNormals();
  const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:ICOL[k]||0x888888,roughness:.5,metalness:.1}));m.visible=false;root.add(m);inner.push(m)}
const box=new THREE.Box3().setFromObject(pivot), ctr=box.getCenter(new THREE.Vector3()), size=box.getSize(new THREE.Vector3()); root.position.sub(ctr);
const R=Math.max(size.x,size.y,size.z);
function shot(name,pos,look,o){o=o||{};
  const hide=o.hide||[]; for(const k in parts){parts[k].m.visible=!hide.includes(k); parts[k].m.material=o.ghost&&k!=='dock_left'&&k!=='dock_right'?parts[k].ghost:parts[k].solid}
  inner.forEach(m=>m.visible=!!o.ghost);
  cam.fov=o.fov||26; cam.updateProjectionMatrix(); cam.position.set(...pos.map(v=>v*R)); cam.lookAt(...look.map(v=>v*R)); ren.render(scene,cam);
  const im=document.createElement('img'); im.id=name; im.setAttribute('data-u',cv.toDataURL('image/png')); document.body.appendChild(im)}
shot('hero',[1.4,.75,2.6],[0,-.02,0]);
shot('open',[1.3,1.0,2.4],[0,-.02,0],{hide:['top_cover']});
shot('inside',[.3,.3,3.1],[0,-.02,0],{ghost:true});
shot('dock',[1.3,.8,1.9],[0,-.36,0],{fov:23});
document.title='done';
</script>''' % (json.dumps(stl), json.dumps(intr), col, icol)
tmp = os.path.join(H, '_capture.html'); open(tmp, 'w', encoding='utf-8').write(PAGE)
E = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
out = subprocess.run([E, '--headless', '--disable-gpu-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--window-size=1600,1000', '--virtual-time-budget=60000', '--dump-dom', 'file:///' + tmp.replace(chr(92), '/')], capture_output=True, timeout=280).stdout.decode('utf-8', 'ignore')
os.remove(tmp)
n = 0
for m in re.finditer(r'<img id="(\w+)" data-u="data:image/png;base64,([^"]+)"', out):
    open(os.path.join(H, 'img', 'v_%s.png' % m.group(1)), 'wb').write(base64.b64decode(m.group(2))); n += 1
print('saved', n)
