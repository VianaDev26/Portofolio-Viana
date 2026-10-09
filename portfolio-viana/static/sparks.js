// FAGULHAS: bolinhas azuis/brancas que sobem pela tela.
// Se a pessoa pediu "menos animação" no aparelho, nada disso roda.
(()=>{const cv=document.getElementById("fx");if(!cv||matchMedia("(prefers-reduced-motion: reduce)").matches)return;
const cx=cv.getContext("2d");let W,H,P=[];
const size=()=>{const d=devicePixelRatio||1;W=innerWidth;H=innerHeight;cv.width=W*d;cv.height=H*d;cx.setTransform(d,0,0,d,0,0)};
// spawn = cria uma fagulha (b = true quando é uma explosão do clique/mouse)
const spawn=(x,y,b)=>P.push({x:x==null?Math.random()*W:x,y:y==null?H+10:y,vx:(Math.random()-.5)*(b?4:.6),vy:-(Math.random()*(b?4:1.3)+.4),r:Math.random()*2.2+.6,life:1,dec:b?.018:.002+Math.random()*.004,hue:[195,205,215,225,210,220][Math.random()*6|0],l:Math.random()<.35?96:62,ph:Math.random()*6});
size();addEventListener("resize",size);
for(let i=0;i<50;i++)spawn(null,Math.random()*H);
// tick = desenha todas as fagulhas, vai se repetindo ~60x por segundo
(function tick(){cx.clearRect(0,0,W,H);if(P.length<90&&Math.random()<.5)spawn();
for(let i=P.length-1;i>=0;i--){const p=P[i];p.ph+=.03;p.x+=p.vx+Math.sin(p.ph)*.3;p.y+=p.vy;p.life-=p.dec;
if(p.life<=0||p.y<-10){P.splice(i,1);continue}
cx.globalAlpha=Math.min(p.life,1);cx.fillStyle="hsl("+p.hue+" 100% "+p.l+"%)";cx.shadowColor="hsl("+p.hue+" 100% 60%)";cx.shadowBlur=12;cx.beginPath();cx.arc(p.x,p.y,p.r,0,6.283);cx.fill()}
requestAnimationFrame(tick)})();
// Clicou na tela: explosão de fagulhas
addEventListener("pointerdown",e=>{for(let i=0;i<22;i++)spawn(e.clientX,e.clientY,true)});
// Mexeu o mouse: solta algumas fagulhas
let lm=0;addEventListener("pointermove",e=>{if(e.timeStamp-lm>40){lm=e.timeStamp;spawn(e.clientX,e.clientY,true)}});
})();
