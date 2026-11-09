"""Approval studies only. Never mutates the active plan, art or engine assets."""
from pathlib import Path
import json, html, math, hashlib
P=Path(__file__).resolve().parent
base=json.loads((P.parent/'proposed-plan.json').read_text())
def obj(name,rect,front=None):return dict(name=name,rect=rect,front=front)
O={
'A':dict(title='Floating sofa · east-wall TV',subtitle='Selected by user · one compact east-facing conversation group.',
 idea='Move the sofa in from the perimeter and turn it toward the east wall. Put the chair at the north end of the same rug, facing the coffee table. The west side stays open to the kitchen.',
 good='The TV sits away from the window, and the chair belongs to the seating group. A clear path runs behind the sofa to the kitchen.',
 tradeoff='The sofa back separates the kitchen approach from the lounge; the room has a stronger east–west division.',
 objects=[obj('Sofa',[8.1,1.2,.84,2.04],'E'),obj('Coffee',[9.4,1.75,.6,1.2]),obj('TV',[11.42,1.5,.46,1.1],'W'),obj('Armchair',[9.4,.6,.749,.689],'S'),obj('Bookcase',[5.65,.3,.4,1.25],'E'),obj('Table + lamp',[8.3,3.4,.37,.351]),obj('Plant',[10.85,.3,.4,.4])],
 rug=[8.8,.9,1.8,2.5],paths=[[[7.05,4.65],[7.05,2.95],[5.15,2.95]],[[10.8,4.65],[10.8,2.2]]],
 eye=[8.52,2.22],screen=[11.42,2.05],gap=[8.94,2.6,9.4,2.6],gap_text='0.46 m',note='Sofa faces east',label=[8.5,3.08],
 strengths='Best for a single sociable group with the TV away from the window.'),
'B':dict(title='Sofa defines the room',subtitle='Alternative · use the open hall as part of the composition.',
 idea='Turn the sofa north and let its low back define the edge of the lounge. Pair it with the chair on the west and a closer coffee table. The TV sits on the north wall to the right of the window.',
 good='The room gains a clear centre. Entry traffic passes behind the sofa, while the kitchen opens onto the side of the seating group. Window, books, seating and the entry repair each provide a different view.',
 tradeoff='The sofa back is visible from the entry. The TV is beside the bright window, so its screen and curtains need a glare check in the lit scene.',
 objects=[obj('Sofa',[8.55,3.15,2.04,.84],'N'),obj('Coffee',[8.97,2.1,1.2,.6]),obj('TV',[9.55,.15,1.1,.46],'S'),obj('Armchair',[7.8,1.9,.689,.749],'E'),obj('Bookcase',[5.65,.3,.4,1.25],'E'),obj('Table + lamp',[8.03,3.25,.37,.351]),obj('Plant',[11.1,.45,.4,.4])],
 rug=[8.3,2.0,2.5,1.8],paths=[[[6.9,4.65],[6.9,2.95],[5.15,2.95]],[[11.1,4.65],[11.1,1.35],[10.3,1.35]]],
 eye=[9.57,3.57],screen=[10.1,.61],gap=[9.55,2.7,9.55,3.15],gap_text='0.45 m',note='Sofa faces north',label=[9.57,3.8],
 strengths='Best balance of a coherent seating group, open kitchen connection and unobstructed entry traffic.'),
'C':dict(title='TV snug + reading corner',subtitle='Two smaller places to settle, with an open approach from the entry.',
 idea='Keep the TV on the kitchen partition but pull the sofa much closer. Move the armchair, lamp and bookcase into a separate corner near the north window.',
 good='The vintage TV has a sensible viewing distance, and the apartment gains a second place to sit and read. The broad east-side approach remains open.',
 tradeoff='The chair is intentionally separate from the sofa. This feels like two intimate zones rather than one larger conversation area.',
 objects=[obj('Sofa',[8.5,1.1,.84,2.04],'W'),obj('Coffee',[7.45,1.3,.6,1.2]),obj('TV',[5.65,1.05,.46,1.1],'E'),obj('Armchair',[9.85,.85,.749,.689],'S'),obj('Bookcase',[11.42,.2,.4,1.25],'W'),obj('Table + lamp',[10.8,1.05,.37,.351]),obj('Plant',[6.45,.2,.4,.4])],
 rug=[6.9,.9,1.8,2.5],paths=[[[6.75,4.65],[6.75,2.95],[5.15,2.95]],[[10.4,4.65],[10.4,2.2]]],
 eye=[8.92,2.12],screen=[6.11,1.60],gap=[8.05,2.0,8.5,2.0],gap_text='0.45 m',note='Sofa faces west',label=[8.92,2.98],
 strengths='Best for a quieter, more collected apartment with distinct TV and reading spots.')}
fixed=[o for o in base['objects'] if o['name'] in ('Entry bench','Fusebox / Wyatt','Hall side console')]
radiator=obj('Radiator',[8.279,.15,.542,.254])
for key,v in O.items():
 v['objects'].append(radiator.copy())
 v['view_distance_m']=round(math.dist(v['eye'],v['screen']),2)
 v['paths']=[[[12,4.65],[5.15,4.65]],*v['paths'],[[11.2,4.65],[11.2,3.7]]]
 v['source_footprints']='Sofa 2.04 x .84; chair .749 x .689; bookcase 1.25 x .40; coffee 1.20 x .60; TV 1.10 x .46; end table .370 x .351 m. Rug stays 2.50 x 1.80 m, rotated where shown.'
 # Check closed footprints and centreline route samples. Rug is intentionally excluded.
 solid=v['objects']+[o for o in fixed if o['name']!='Fusebox / Wyatt']
 for i,a in enumerate(solid):
  for b in solid[i+1:]:
   x,y,w,h=a['rect'];xx,yy,ww,hh=b['rect']
   assert not (min(x+w,xx+ww)>max(x,xx)+1e-6 and min(y+h,yy+hh)>max(y,yy)+1e-6),(key,a['name'],b['name'])
 for a in v['objects']:
  x,y,w,h=a['rect'];assert x>=5.56 and x+w<=11.94 and y>=.06 and y+h<=5.54,(key,a['name'],'shell')
 minimum=(99,'')
 for path in v['paths']:
  for a,b in zip(path,path[1:]):
   for j in range(201):
    t=j/200;px=a[0]+(b[0]-a[0])*t;py=a[1]+(b[1]-a[1])*t
    for o in solid:
     x,y,w,h=o['rect'];dist=math.hypot(max(x-px,0,px-x-w),max(y-py,0,py-y-h))
     if dist<minimum[0]:minimum=(dist,o['name'])
 assert minimum[0]>=.35,(key,minimum)
 v['route_sample_min_distance_m']=round(minimum[0],3)
 print(key,'view distance',v['view_distance_m'],'route margin',minimum)
(P/'options.json').write_text(json.dumps({'status':'User selected A; applied to the full revision-02 floor plan','base_plan_sha256':hashlib.sha256((P.parent/'proposed-plan.json').read_bytes()).hexdigest(),'initial_recommendation':'B','selected':'A','fixed':fixed,'options':O},indent=2)+'\n')

S=88;OX=76;OY=72
X=lambda x: OX+(x-5.5)*S
Y=lambda y: OY+y*S
E=html.escape
def svg(key,v,thumb=False):
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 650" role="img" aria-label="Living room option '+key+'" style="font-family:Arial,sans-serif"><defs><marker id="arrow'+key+'" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10" fill="none" stroke="#287c75" stroke-width="2"/></marker></defs><rect width="760" height="650" fill="#faf6ed"/>']
 def txt(x,y,t,size=12,c='#403b34',anchor='middle',weight='normal'):
  out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{c}" font-weight="{weight}">{E(t)}</text>')
 def line(x,y,xx,yy,c='#584c40',w=8,dash=''):
  out.append(f'<line x1="{X(x)}" y1="{Y(y)}" x2="{X(xx)}" y2="{Y(yy)}" stroke="{c}" stroke-width="{w}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def rect(r,fill,stroke='#8f7e6d',sw=1,rx=0):
  x,y,w,h=r;out.append(f'<rect x="{X(x)}" y="{Y(y)}" width="{w*S}" height="{h*S}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 txt(34,30,key+'  '+v['title'],20,anchor='start',weight='bold')
 txt(34,52,'North ↑ · same furniture scale and room boundaries in every option',11,anchor='start')
 rect([5.5,0,6.5,5.6],'#efcfaa',sw=0)
 rect([5.5,4.15,6.5,.95],'#e7ddc7',sw=0)
 rect(v['rug'],'#b8907e','#9a7868',1,6)
 # Floor-plan front directions are independent of any FBX yaw convention.
 for o in v['objects']+fixed:
  x,y,w,h=o['rect'];n=o['name'];front=o.get('front');fill='#fff7e7'
  if n in ('Sofa','Armchair'):fill='#bd8d7f'
  if n=='Plant':
   out.append(f'<circle cx="{X(x+w/2)}" cy="{Y(y+h/2)}" r="{w*S/2}" fill="#809475" stroke="#59684f"/>')
  else:rect(o['rect'],fill,rx=3)
  if n in ('Sofa','Armchair'):
   # Back strip and cushion layout make seating orientation visible at a glance.
   if front=='N':rect([x+.06,y+h-.13,w-.12,.07],'#94675a',sw=0)
   if front=='S':rect([x+.06,y+.06,w-.12,.07],'#94675a',sw=0)
   if front=='E':rect([x+.06,y+.06,.07,h-.12],'#94675a',sw=0)
   if front=='W':rect([x+w-.13,y+.06,.07,h-.12],'#94675a',sw=0)
   cx=x+w/2;cy=y+h/2;dx,dy={'N':(0,-1),'S':(0,1),'E':(1,0),'W':(-1,0)}[front]
   line(cx,cy,cx+dx*.2,cy+dy*.2,'#6b493e',2)
   tx=cx+dx*.2;ty=cy+dy*.2
   if dx:line(tx,ty,tx-dx*.07,ty-.06,'#6b493e',2);line(tx,ty,tx-dx*.07,ty+.06,'#6b493e',2)
   else:line(tx,ty,tx-.06,ty-dy*.07,'#6b493e',2);line(tx,ty,tx+.06,ty-dy*.07,'#6b493e',2)
  if n=='TV':
   if front=='W':line(x,y+.12,x,y+h-.12,'#725075',4)
   if front=='E':line(x+w,y+.12,x+w,y+h-.12,'#725075',4)
   if front=='S':line(x+.12,y+h,x+w-.12,y+h,'#725075',4)
  if not thumb:
   if n=='Fusebox / Wyatt':txt(X(x)-9,Y(y+h/2)+4,'Fuse / Wyatt',10,anchor='end')
   elif n=='Table + lamp':
    out.append(f'<circle cx="{X(x+w/2)}" cy="{Y(y+h/2)}" r="9" fill="#e6c27b" stroke="#937847"/>')
    txt(X(x+w/2),Y(y+h)+13,'Lamp',10)
   elif n in ('Bookcase','Entry bench'):
    out.append(f'<text transform="translate({X(x+w/2)} {Y(y+h/2)}) rotate(-90)" text-anchor="middle" font-size="11" fill="#403b34">{E(n.replace("Entry ",""))}</text>')
   elif n=='Sofa':txt(X(x+w/2),Y(y+h/2)+(16 if front=='N' else -12),'Sofa',12,weight='bold')
   elif n=='Armchair':txt(X(x+w/2),Y(y+h/2)-12,'Chair',10)
   elif n!='Plant':txt(X(x+w/2),Y(y+h/2)+4,{'Hall side console':'Hall console'}.get(n,n),10)
 # Walls, apertures and adjacent-room labels.
 line(5.5,0,12,0);line(5.5,0,5.5,2.35);line(5.5,3.55,5.5,3.8)
 line(12,0,12,4);line(12,5.05,12,5.6);line(5.5,5.6,12,5.6)
 line(7.75,0,9.35,0,'#acd0d5',11);line(7.75,0,9.35,0,'#fff',2)
 line(5.5,3.8,12,3.8,'#a58c72',1.5,'5 5')
 for a,b in [(6.25,7.3),(9.45,10.5),(10.93,11.83)]:line(a,5.6,b,5.6,'#faf6ed',11)
 for a,b in [(6.25,7.3),(9.45,10.5)]:
  line(a,5.6,a,5.9,'#9a7959',2)
 line(10.93,5.575,11.43,5.575,'#9a7959',2);line(11.33,5.625,11.83,5.625,'#9a7959',2)
 line(12,4,12.7,4,'#9a7959',2)
 out.append(f'<path d="M {X(12)} {Y(5.05)} A {1.05*S} {1.05*S} 0 0 0 {X(13.05)} {Y(4)}" fill="none" stroke="#9a7959" stroke-width="1.5"/>')
 # Clip external landing arc to view rather than imply a designed landing.
 for path in v['paths']:
  pts=' '.join(f'{X(x)},{Y(y)}' for x,y in path)
  out.append(f'<polyline points="{pts}" fill="none" stroke="#287c75" stroke-width="2.5" opacity=".78" marker-end="url(#arrow{key})"/>')
 if not thumb:
  txt(X(5.35),Y(2.75),'TO',10,anchor='end');txt(X(5.35),Y(2.95),'KITCHEN',10,anchor='end')
  txt(X(12.1),Y(5.32),'ENTRY',11,anchor='start',weight='bold')
  txt(X(6.78),Y(5.95),'BATH',11);txt(X(9.98),Y(5.95),'OFFICE',11);txt(X(11.38),Y(5.95),'COATS',11)
  txt(X(7.6),Y(4.96),'ENTRY → PRIVATE HALL',11)
  # Dimension the coffee gap; no line crossing the sofa or table.
  x,y,xx,yy=v['gap'];line(x,y,xx,yy,'#76547c',1.5)
  if y==yy:txt(X((x+xx)/2),Y(y)-6,v['gap_text'],10,c='#67486e')
  else:txt(X(x)+7,Y((y+yy)/2)+4,v['gap_text'],10,c='#67486e',anchor='start')
  if key=='B':
   line(8.73,3.99,8.73,5.27,'#76547c',1.3)
   txt(X(8.73)-7,Y(4.38),'1.28 m behind sofa',10,c='#67486e',anchor='end')
  txt(34,620,'Teal: walking routes · seat arrows: facing · dashed line: overhead opening',11,anchor='start')
  txt(34,640,'Planning study only. Collision, upholstery bounds and camera movement need engine checks.',11,anchor='start')
 out.append('</svg>');return ''.join(out)
for key,v in O.items():(P/f'option-{key.lower()}.svg').write_text(svg(key,v))
# All options are present in the HTML; buttons only change which is visible.
page='''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;font-family:var(--font-sans,Arial,sans-serif);color:var(--foreground)}p{font-size:14px;line-height:1.5;margin:8px 0 12px}.buttons{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}button{font:inherit;border:1px solid var(--border);border-radius:var(--radius,8px);background:var(--secondary);color:var(--foreground);padding:9px 12px;cursor:pointer}button.active{background:var(--primary);color:var(--primary-foreground)}.plan{overflow:hidden;border-radius:var(--radius,8px)}svg{display:block;width:100%;height:auto}.hidden{display:none}.tag{font-size:13px;color:var(--muted-foreground)}.thumbs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:18px}.thumbs button{padding:0;overflow:hidden;text-align:left}.thumbs span{display:block;padding:8px;font-size:12px}.notes{background:var(--card);border-radius:var(--radius,8px);padding:16px;margin:12px 0}.notes p:last-child{margin-bottom:0}
</style></head><body><p>The current group spreads a small TV and sofa too far apart. These studies bring the seating together and give the open entry a clearer relationship to the room.</p><div class="buttons">'''
for k,v in O.items():page+=f'<button id="button-{k}" class="'+('active' if k=='A' else '')+f'" onclick="pick(\'{k}\')">{k} · '+{'A':'East-facing lounge · selected','B':'Sofa defines room','C':'TV + reading corner'}[k]+'</button>'
page+='</div>'
for k,v in O.items():
 page+=f'<section id="option-{k}" class="'+('' if k=='A' else 'hidden')+'"><p class="tag">'+E(v['subtitle'])+'</p><div class="plan">'+svg(k,v)+'</div><div class="notes"><p>'+E(v['idea'])+'</p><p><strong>Why it works:</strong> '+E(v['good'])+'</p><p><strong>Tradeoff:</strong> '+E(v['tradeoff'])+f'</p><p class="tag">Approx. seat-to-screen distance: {v["view_distance_m"]:.1f} m · sofa-to-table gap: {v["gap_text"]} · existing rug size retained.</p></div></section>'
page+='<div class="thumbs">'
for k,v in O.items():page+=f'<button onclick="pick(\'{k}\')" aria-label="Select option {k}">'+svg(k,v,True)+f'<span><strong>{k}</strong> · '+E(v['title'])+'</span></button>'
page+='''</div><p><strong>Option A was selected by the user.</strong> Its east-facing sofa, east-wall TV and north-end chair are now incorporated into the full floor plan. B and C remain here for comparison history.</p><p class="tag">The closet, wainscoting, fusebox and hallway-console decisions remain as proposed. Option A has been applied to the revision-02 floor plan. Elevations and game placement have not changed.</p><script>function pick(k){for(const q of ['A','B','C']){document.getElementById('option-'+q).classList.toggle('hidden',q!==k);document.getElementById('button-'+q).classList.toggle('active',q===k)}}</script></body></html>'''
(P/'review.html').write_text(page)
