function rr(c,x,y,w,h,r){c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath()}
function draw(now){
  const dt=Math.min(.05,(now-last)/1000);last=now;
  const dp=dpOf(Q), sat=dp>=SAT, load=Math.min(1,dp/SAT);
  const ink=css("--ink"),mute=css("--mute"),sky=css("--sky"),skyd=css("--sky-d"),panel=css("--panel"),hot=css("--hot"),
        mint=css("--mint"),peach=css("--peach"),lilac=css("--lilac"),sun=css("--sun"),air=css("--air");
  const F=getComputedStyle(document.body).fontFamily, FD=getComputedStyle(document.documentElement).getPropertyValue("--disp");
  cx.clearRect(0,0,W,H);
  // soft background clouds
  cx.globalAlpha=.5;cx.fillStyle=sky;[[120,70,34],[170,86,24],[980,360,38],[930,380,26]].forEach(c=>{cx.beginPath();cx.arc(c[0],c[1],c[2],0,7);cx.fill()});cx.globalAlpha=1;
  // ---- puffy glass tube: draw the lumen as a smooth rounded body
  cx.save();cx.shadowColor="rgba(40,100,170,.35)";cx.shadowBlur=26;cx.shadowOffsetY=14;
  cx.beginPath();
  for(let x=0;x<=170;x+=1){const r=rad(x)+3.2;x?cx.lineTo(px(x),py(-r)):cx.moveTo(px(x),py(-r))}
  for(let x=170;x>=0;x-=1){cx.lineTo(px(x),py(rad(x)+3.2))}
  cx.closePath();cx.fillStyle=panel;cx.fill();cx.restore();
  // rings
  for(const [a,b] of [[21,25],[150,153]]){cx.fillStyle=sky;rr(cx,px(a),py(-21),(b-a)*S+2,42*S,5);cx.fill()}
  // lumen: pressure drawn as warm tint (more pressure drop = warmer)
  for(let i=0;i<170;i++){const x=i,r=rad(x+.5),p=pressureAt(x+.5,Math.min(dp,SAT));
    const t=Math.min(1,Math.abs(p)/SAT);
    cx.fillStyle=air;cx.fillRect(px(x),py(-r),S+.7,2*r*S);
    cx.globalAlpha=.12+.8*t;cx.fillStyle=peach;cx.fillRect(px(x),py(-r),S+.7,2*r*S);cx.globalAlpha=1}
  // glossy highlight along the top
  const hg=cx.createLinearGradient(0,py(-14),0,py(-4));hg.addColorStop(0,"rgba(255,255,255,.75)");hg.addColorStop(1,"rgba(255,255,255,0)");
  cx.fillStyle=hg;cx.beginPath();
  for(let x=2;x<=168;x+=1){const r=rad(x);x>2?cx.lineTo(px(x),py(-r+1.6)):cx.moveTo(px(x),py(-r+1.6))}
  for(let x=168;x>=2;x-=1){cx.lineTo(px(x),py(-rad(x)*.45))}
  cx.closePath();cx.fill();
  // outline
  cx.strokeStyle=skyd;cx.lineWidth=3;cx.lineJoin="round";cx.beginPath();
  for(let x=0;x<=170;x+=1){const r=rad(x);x?cx.lineTo(px(x),py(-r)):cx.moveTo(px(x),py(-r))}
  for(let x=170;x>=0;x-=1){cx.lineTo(px(x),py(rad(x)))}
  cx.closePath();cx.stroke();
  // ---- air puffs: little round bubbles, faster where the tube is narrow
  const v0=Q/1000/(Math.PI*0.014**2);
  for(const p of P){const r=rad(p.x),v=v0*(14/r)**2;
    p.x+=v*dt*14; if(p.x>170){p.x=0;p.f=(Math.random()*2-1)*.88}
    const y=py(p.f*rad(p.x)),sz=2.6+(14/r-1)*3.5,X=px(p.x);
    const g=cx.createRadialGradient(X-1,y-1,0,X,y,sz*1.6);g.addColorStop(0,"#ffffff");g.addColorStop(.6,sky);g.addColorStop(1,skyd);
    cx.globalAlpha=.9;cx.fillStyle=g;cx.beginPath();cx.arc(X,y,sz,0,7);cx.fill();cx.globalAlpha=1}
  // ---- labels
  cx.fillStyle=mute;cx.font="600 15px "+F;cx.textAlign="center";
  cx.fillText("ปากเป่า",px(10),py(-27));cx.fillText("ท่อ Ø28",px(40),py(-27));
  cx.fillText("คอคอด Ø23",px((X_THR0+X_THR1)/2),py(-27));cx.fillText("ทางออก",px(140),py(-27));
  // ---- manifold block (rounded puffy)
  const bx=px(49),by=py(17),bw=(86-49)*S,bh=(26-17)*S+4;
  cx.save();cx.shadowColor="rgba(40,100,170,.3)";cx.shadowBlur=14;cx.shadowOffsetY=8;cx.fillStyle=panel;rr(cx,bx,by,bw,bh,14);cx.fill();cx.restore();
  cx.strokeStyle=sky;cx.lineWidth=2.5;rr(cx,bx,by,bw,bh,14);cx.stroke();
  cx.fillStyle=mute;cx.font="12px "+F;cx.textAlign="left";cx.fillText("บล็อกต่อท่อ (พิมพ์ในตัว)",px(50),py(36));
  // channels as soft rounded pipes
  const pipe=(pts,col)=>{cx.lineCap="round";cx.lineJoin="round";cx.strokeStyle=col;cx.lineWidth=9;cx.beginPath();
    pts.forEach((q,i)=>i?cx.lineTo(q[0],q[1]):cx.moveTo(q[0],q[1]));cx.stroke();
    cx.strokeStyle="rgba(255,255,255,.7)";cx.lineWidth=3;cx.beginPath();pts.forEach((q,i)=>i?cx.lineTo(q[0]-1,q[1]-1):cx.moveTo(q[0]-1,q[1]-1));cx.stroke()};
  const yCh=py(24);
  pipe([[px(TAP1),py(14)],[px(TAP1),yCh],[px(BARB1),yCh],[px(BARB1),py(43)]],hot);
  pipe([[px(TAP2),py(11.5)],[px(TAP2),py(43)]],skyd);
  // ---- sensor chip with a face
  const sx=px(TAP2-17),sy=py(46),sw=26*S,sh=62;
  cx.save();cx.shadowColor="rgba(40,100,170,.35)";cx.shadowBlur=16;cx.shadowOffsetY=9;
  const cg=cx.createLinearGradient(0,sy,0,sy+sh);cg.addColorStop(0,sat?hot:lilac);cg.addColorStop(1,sat?peach:skyd);
  cx.fillStyle=cg;rr(cx,sx,sy,sw,sh,20);cx.fill();cx.restore();
  cx.fillStyle="rgba(255,255,255,.35)";rr(cx,sx+8,sy+6,sw-16,12,6);cx.fill();
  // eyes + mouth react to load
  const ex1=sx+sw*.34,ex2=sx+sw*.66,ey=sy+30;
  cx.fillStyle="#1e3250";
  if(sat){cx.lineWidth=3;cx.strokeStyle="#1e3250";[ex1,ex2].forEach(e=>{cx.beginPath();cx.moveTo(e-5,ey-4);cx.lineTo(e+5,ey+4);cx.moveTo(e+5,ey-4);cx.lineTo(e-5,ey+4);cx.stroke()});
    cx.beginPath();cx.arc(sx+sw/2,ey+19,6,0,7);cx.stroke()}
  else{[ex1,ex2].forEach(e=>{cx.beginPath();cx.ellipse(e,ey,5,dp<DEAD?2:6.5,0,0,7);cx.fill()});
    cx.lineWidth=3;cx.strokeStyle="#1e3250";cx.beginPath();
    if(dp<DEAD)cx.arc(sx+sw/2,ey+14,7,.15*Math.PI,.85*Math.PI);else cx.arc(sx+sw/2,ey+8,9,.15*Math.PI,.85*Math.PI);cx.stroke()}
  cx.fillStyle="#fff";cx.font="700 13px "+FD;cx.textAlign="center";cx.fillText("SDP810",sx+sw/2,sy+sh+18);
  // load meter (pill)
  const mx=sx+sw+26,my=sy+8;
  cx.fillStyle=panel;rr(cx,mx,my,200,20,10);cx.fill();cx.strokeStyle=sky;cx.lineWidth=2;rr(cx,mx,my,200,20,10);cx.stroke();
  if(load>0.01){const mg=cx.createLinearGradient(mx,0,mx+200,0);mg.addColorStop(0,mint);mg.addColorStop(.6,sun);mg.addColorStop(1,hot);
    cx.save();rr(cx,mx+2,my+2,196,16,8);cx.clip();cx.fillStyle=mg;cx.fillRect(mx+2,my+2,196*load,16);cx.restore()}
  cx.fillStyle=mute;cx.font="12px "+F;cx.textAlign="left";cx.fillText("ความดันต่าง "+dp.toFixed(1)+" Pa จากเต็ม 500",mx,my+40);
  // ESP32 chip
  const ex=mx+250,eyy=sy-4;
  cx.save();cx.shadowColor="rgba(40,100,170,.3)";cx.shadowBlur=14;cx.shadowOffsetY=8;cx.fillStyle=panel;rr(cx,ex,eyy,150,64,18);cx.fill();cx.restore();
  cx.strokeStyle=mint;cx.lineWidth=3;rr(cx,ex,eyy,150,64,18);cx.stroke();
  cx.fillStyle=ink;cx.textAlign="center";cx.font="600 15px "+FD;cx.fillText("XIAO ESP32",ex+75,eyy+28);
  cx.font="12px "+F;cx.fillStyle=mute;cx.fillText("BLE · Wi-Fi",ex+75,eyy+47);
  cx.strokeStyle=mute;cx.lineWidth=2;cx.setLineDash([2,7]);cx.lineCap="round";
  cx.beginPath();cx.moveTo(sx+sw,sy+sh/2);cx.lineTo(mx-4,sy+sh/2);cx.moveTo(mx+206,sy+sh/2);cx.lineTo(ex,sy+sh/2);cx.stroke();cx.setLineDash([]);
  // legend
  cx.textAlign="left";cx.font="12px "+F;
  cx.fillStyle=hot;cx.beginPath();cx.arc(px(2)+6,py(53),6,0,7);cx.fill();cx.fillStyle=mute;cx.fillText("ความดันสูง (ก่อนคอคอด)",px(2)+18,py(53)+4);
  cx.fillStyle=skyd;cx.beginPath();cx.arc(px(2)+6,py(53)+22,6,0,7);cx.fill();cx.fillStyle=mute;cx.fillText("ความดันต่ำ (ที่คอคอด)",px(2)+18,py(53)+26);
  readouts();
  requestAnimationFrame(draw);
}
