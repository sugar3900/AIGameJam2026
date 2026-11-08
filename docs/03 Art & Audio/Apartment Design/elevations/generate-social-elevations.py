from pathlib import Path
from xml.sax.saxutils import escape
out=Path(__file__).resolve().parent
S=125; X=130; H=2.75*S; F=410; STEP=475
colors={'wall':'#e8d6b8','wood':'#8b5338','darkwood':'#593e32','sage':'#a5ad7a','white':'#f4e6c8','pink':'#cb8481','dark':'#574437','cloth':'#a4a77d','metal':'#746a5d','rust':'#ac6549','glass':'#9fb6a5','tile':'#d5b39a'}
def rect(x,y,w,h,fill,stroke='#634c3d',sw=2,rx=0,extra=''): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'
def line(x1,y1,x2,y2,c='#634c3d',sw=2,extra=''): return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{sw}" {extra}/>'
def text(x,y,t,size=12,anchor='middle',c='#493b33',extra=''): return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {extra}>{escape(t)}</text>'
def circ(x,y,r,fill,stroke='#634c3d',sw=1.5):return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
class Wall:
 def __init__(self, wid, title, width, row, palette='wall'):
  self.id=wid;self.width=width;self.reverse=wid.endswith(('-S','-W'));self.y=row*STEP;self.f=self.y+F; self.a=[]; self.a.append(text(X,self.y+32,f'{wid}  •  {title}  •  {width:.2f} m',20,'start',extra='font-weight="bold"')); self.a.append(rect(X,self.f-H,width*S,H,colors[palette],sw=2));self.a.append(rect(X,self.f-16,width*S,16,'#d4bd99',sw=1));self.a.append(rect(X,self.f-H,width*S,12,'#f3dfba',sw=1));self.a.append(line(X,self.f+23,X+width*S,self.f+23,'#a76a56'));self.a.append(text(X+width*S/2,self.f+42,f'{width:.2f} m wall  |  2.75 m ceiling',11));
 def R(self,x,z,w,h,fill,stroke='#634c3d',sw=2,rx=0,extra=''):
  if self.reverse:x=self.width-x-w
  self.a.append(rect(X+x*S,self.f-(z+h)*S,w*S,h*S,fill,stroke,sw,rx,extra))
 def L(self,x,z,x2,z2,c='#634c3d',sw=2,extra=''):
  if self.reverse:x,x2=self.width-x,self.width-x2
  self.a.append(line(X+x*S,self.f-z*S,X+x2*S,self.f-z2*S,c,sw,extra))
 def C(self,x,z,r,fill,stroke='#634c3d'):
  if self.reverse:x=self.width-x
  self.a.append(circ(X+x*S,self.f-z*S,r*S,fill,stroke))
 def T(self,x,z,t,size=10,c='#493b33',anchor='middle'):
  if self.reverse:x=self.width-x
  self.a.append(text(X+x*S,self.f-z*S,t,size,anchor,c))
 def label(self,x,z,t): self.T(x,z,t,10,'#49352d')
 def door(self,x,w=.9,label='door'):
  self.R(x,0,w,2.10,'#826752');self.R(x+.055,.04,w-.11,2.0,'#d8c5a5');self.R(x+.11,.17,w-.22,.72,'none','#98795b',1);self.R(x+.11,1.02,w-.22,.84,'none','#98795b',1);self.C(x+w-.14,1.0,.025,'#b39155');self.label(x+w/2,2.18,label+' · swing')
 def opening(self,x,w=.9,label='opening'):
  self.R(x,0,w,2.1,'#998876');self.R(x+.04,.03,w-.08,2.03,'#e3d7bd');self.label(x+w/2,2.18,label)
 def window(self,x,w,sill=.9,head=2.3,label='window'):
  self.R(x,sill,w,head-sill,'#aec1ad');self.R(x+.08,sill+.08,w-.16,head-sill-.16,'#b9c9b3');self.L(x+w/2,sill+.08,x+w/2,head-.08,'#eee0c4',5);self.L(x+.08,(sill+head)/2,x+w-.08,(sill+head)/2,'#eee0c4',4);self.R(x-.04,sill-.06,w+.08,.08,'#ebd5b1');self.R(x-.07,head+.04,w+.14,.05,colors['wood']);self.label(x+w/2,head+.15,label)
 def frame(self,x,z,w=.4,h=.4,name='picture'):
  self.R(x,z,w,h,colors['wood']);self.R(x+.035,z+.035,w-.07,h-.07,'#e4c989');self.R(x+.07,z+.07,w-.14,h-.14,'#a4b18d',sw=1);self.label(x+w/2,z+h+.10,name)
 def shelf(self,x,z,w,books=True):
  self.R(x,z,w,.05,colors['wood']);
  if books:
   for i,col in enumerate(['#a97054','#d1b77e','#768f7c','#b49172','#8a604a']):self.R(x+.03+i*.075,z+.05,.06,.23+(i%3)*.03,col,sw=.5)
 def curtain(self,x,w,sill=.9,head=2.3):
  self.R(x-.12,sill-.02,.17,head-sill+.08,'#bf8d79',sw=1);self.R(x+w-.05,sill-.02,.17,head-sill+.08,'#bf8d79',sw=1)
  for p in [x-.08,x+.00,x+w-.01,x+w+.07]:self.L(p,sill+.02,p,head+.02,'#e7c3a5',1)
 def plant(self,x,z=0):
  self.R(x,z,.22,.22,'#b4775a',sw=1);self.L(x+.11,z+.21,x+.11,z+.55,'#526d4e',3)
  for dx,dz in [(-.11,.40),(.12,.46),(-.08,.55),(.09,.62)]:
   px=x+.11+dx; px=self.width-px if self.reverse else px; cx=X+px*S; cy=self.f-(z+dz)*S
   self.a.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="11" ry="5" transform="rotate(-25 {cx:.1f} {cy:.1f})" fill="#718965"/>')
 def note(self, t):self.a.append(text(X+15,self.y+65,t,11,'start','#8c4e43'))
def svg(name,walls,summary):
 W=max(w.width for w in walls)*S+260; ht=len(walls)*STEP+110
 a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{ht:.0f}" viewBox="0 0 {W:.0f} {ht:.0f}">',f'<rect width="100%" height="100%" fill="#f7f1e5"/>',f'<g font-family="Arial, sans-serif">']
 for wall in walls:a+=wall.a
 a.append(text(X,len(walls)*STEP+14,summary,12,'start'));a.append(text(X,len(walls)*STEP+34,'View toward wall: N west → east; E north → south; S east → west; W south → north. Foreground items shown in projection.',11,'start'));a.append(text(X,len(walls)*STEP+54,'Planning drawing; opening positions from A-plus-candidate.json, verify clearances and details in 3D.',11,'start'));a.append('</g></svg>');(out/name).write_text('\n'.join(a))
# LIVING north: window x1.35, shelf x3.55, chair in front
n=Wall('LV-N','Window wall, facing north',5.5,0);n.window(1.35,1.6,label='LV-WIN-01 sash');n.curtain(1.35,1.6);n.R(3.55,0,1.25,1.85,colors['wood']);
for z in [.28,.66,1.04,1.42,1.77]:n.shelf(3.60,z,1.15)
n.label(4.17,1.97,'LV-BOOK-01 bookcase + books');n.R(1.20,0,.75,.75,colors['rust'],rx=10);n.R(1.26,.54,.63,.36,'#ba8067',rx=14);n.label(1.57,.83,'LV-CHAIR-01 armchair');n.plant(4.9);n.label(5.0,.82,'LV-PLANT-01');n.R(2.16,0,.65,.60,'#d3c5a6');
for x in [2.23,2.33,2.43,2.53,2.63,2.73]:n.L(x,.08,x,.52,'#9b927c',2)
n.label(2.49,.70,'LV-RAD-01 radiator');n.note('Chair is in front of the window; radiator fits against wall between chair and bookcase.')
e=Wall('LV-E','TV wall, facing east',3.8,1);e.R(1.25,0,1.1,.55,colors['wood']);e.R(1.31,.1,.46,.32,'#a56b45');e.R(1.83,.1,.46,.32,'#a56b45');e.C(1.7,.26,.025,'#cfad70');e.C(2.22,.26,.025,'#cfad70');e.R(1.35,.62,.90,.72,colors['darkwood'],rx=8);e.R(1.40,.70,.80,.52,'#4d5150',rx=6);e.C(2.19,.67,.025,'#ccae74');e.label(1.8,1.47,'LV-TV-01 TV + console · on/off');e.frame(.18,1.50,.52,.42,'LV-ART-01');e.frame(2.75,1.53,.42,.55,'LV-ART-02');e.plant(3.35);e.label(3.48,.82,'LV-PLANT-02');e.R(.15,0,.62,.63,'#b78765',rx=5);e.label(.45,.72,'LV-BOX-01 stack')
s=Wall('LV-S','Hall entrance and fuse wall, facing south',5.5,2);s.door(4.05,.9,'LV-DR-01');s.R(2.9,1.12,.45,.65,colors['metal']);s.R(2.94,1.16,.37,.57,'#a7a097');s.L(2.97,1.45,3.26,1.45);s.C(3.17,1.58,.035,'#d8ba75');s.label(3.12,1.9,'LV-FUSE-01 open / repaired');s.L(3.05,1.77,3.05,2.42,'#8a5b4a',3);s.frame(.32,1.32,.53,.50,'LV-ART-03');s.R(1.22,0,.90,.40,colors['wood']);s.R(1.27,.08,.8,.24,'#a67a5a');s.label(1.67,.52,'LV-CHEST-01');s.R(1.45,.41,.38,.12,'#c5b089');s.label(1.64,.65,'LV-BOOKS-01');s.L(2.95,1.76,2.83,1.88,'#b58069',1);s.L(2.83,1.88,2.89,2.04,'#b58069',1);s.L(3.35,1.16,3.46,1.08,'#b58069',1);s.L(3.46,1.08,3.52,.96,'#b58069',1);s.label(3.67,1.08,'LV-FUSE-DAMAGE-01');s.note('Fuse door and damaged/repaired interior remain unobstructed.')
w=Wall('LV-W','Sofa wall, facing west',3.8,3);w.R(.8,0,2.0,.75,'#8d9971',rx=15);w.R(.87,.48,.56,.28,'#a7ae83',rx=8);w.R(1.47,.48,.56,.28,'#9daa80',rx=8);w.R(2.07,.48,.56,.28,'#a9ae80',rx=8);w.R(.83,.10,.58,.25,'#b99a7d',rx=5);w.R(2.23,.10,.48,.24,'#c49a8c',rx=5);w.label(1.8,.90,'LV-SOFA-01 sofa / LV-CUSH-01 cushions');w.frame(1.25,1.38,.72,.52,'LV-ART-04 landscape');w.R(.15,0,.37,.54,colors['wood']);w.R(.23,.55,.22,.04,'#dbb66c');w.R(.28,.59,.08,.30,'#b4925a');w.R(.18,.89,.28,.22,'#e5ca8b',rx=8);w.label(.35,1.22,'LV-LAMP-01 on/off');w.R(2.95,0,.45,.48,colors['wood']);w.plant(3.07,.48);w.label(3.18,1.23,'LV-PLANT-03');w.note('Coffee table LV-TABLE-01 and rug LV-RUG-01 occupy foreground; not against wall.')
svg('01-living-elevations.svg',[n,e,s,w],'Living room: LV-RUG-01 floral rug; LV-TABLE-01 coffee table; books, frames and plants provide layered detail.')
# KITCHEN north frontage
n=Wall('KI-N','Sink, range and refrigerator wall',6.5,0);n.R(0,0,6.5,.12,'#b18d70',sw=1);n.R(0,.88,6.5,.56,'url(#tile)',sw=1);n.window(2.5,1.1,label='KI-WIN-01 sash');n.curtain(2.5,1.1);n.R(.12,0,.75,1.72,'#ece0bc',rx=12);n.L(.14,.85,.85,.85);n.R(.18,.97,.04,.32,'#9b907a');n.R(.18,.27,.04,.31,'#9b907a');n.label(.5,1.86,'KI-FRIDGE-01 door rotates');n.R(1.0,0,.75,.88,'#e5d4af',rx=5);n.R(1.08,.12,.59,.45,'#9b9a83');n.R(1.04,.78,.67,.10,'#d1bd96');
for xx in [1.12,1.27,1.42,1.57]:n.C(xx,.72,.027,'#a99a7b')
n.label(1.37,1.0,'KI-RANGE-01 oven');n.R(1.78,0,.65,.86,colors['sage']);n.R(2.46,0,1.05,.77,colors['sage']);n.R(2.42,.72,1.13,.14,'#f0dfbc');n.R(2.54,.80,.89,.12,'#ddd3b9');n.L(2.97,.92,2.97,1.12,'#9a9b92',5);n.L(2.97,1.12,3.13,1.12,'#9a9b92',5);n.R(3.55,0,1.15,.86,colors['sage']);
for x,wid in [(1.78,.65),(2.46,.50),(2.97,.54),(3.55,.55),(4.12,.58)]:n.R(x+.04,.07,wid-.08,.55,'none','#80875a',1);n.C(x+wid-.12,.62,.025,'#e5d8ba')
n.R(1.78,.85,2.92,.06,'#ecdcb9');n.label(3.03,.61,'KI-SINK-01 leak / fixed · KI-CAB-01 drawers');n.R(3.70,1.60,1.0,.55,colors['sage']);n.L(4.2,1.60,4.2,2.15);n.C(4.12,1.85,.02,'#e5d6b3');n.C(4.28,1.85,.02,'#e5d6b3');n.label(4.2,2.27,'KI-UPPER-01 doors');n.R(2.48,.05,.18,.3,'#abb2ac',rx=3);n.label(2.57,.43,'KI-BUCKET-01');n.R(5.7,0,.67,1.98,colors['sage']);n.label(6.04,2.1,'KI-PANTRY-01 side');n.R(1.25,.89,.24,.13,'#d5ad68',rx=8);n.C(1.37,1.02,.06,'#d5ad68');n.label(1.37,1.23,'KI-KETTLE-01');n.C(1.95,1.68,.13,'#987455');n.C(2.25,1.68,.13,'#ad8c68');n.L(1.95,1.81,1.95,2.01);n.L(2.25,1.81,2.25,2.01);n.label(2.1,2.12,'KI-PANS-01');n.plant(3.21,.97);n.label(3.30,1.78,'KI-PLANT-01');n.note('Window 1.10 m; sink below. Cabinets, enamel, backsplash and age marks remain discrete.')
e=Wall('KI-E','Dining and pantry return, facing east',3.8,1);e.R(.12,0,1.0,2.0,colors['sage']);e.L(.62,.1,.62,1.9);e.C(.53,1.0,.02,'#dcd1ae');e.C(.71,1.0,.02,'#dcd1ae');e.label(.62,2.12,'KI-PANTRY-01 hinged');e.frame(1.55,1.4,.60,.45,'KI-ART-01');e.shelf(2.35,1.72,.9,False);e.R(2.45,1.77,.15,.21,'#d2b37f',rx=4);e.R(2.64,1.77,.16,.27,'#c58d79',rx=4);e.R(2.84,1.77,.17,.19,'#e5d7b3',rx=4);e.label(2.80,2.10,'KI-SHELF-01 jars');e.R(1.48,2.0,.09,.17,'#bb9967',rx=3);e.C(1.525,1.96,.065,'#f2d292');e.label(1.52,2.25,'KI-SCONCE-01');e.note('Pantry at north end; wall art, sconce and shelf preserve coat-closet return and clear floor.')
s=Wall('KI-S','Hall door and coat closet back, facing south',6.5,2);s.door(.7,.9,'KI-DR-01');s.R(5.2,0,1.3,2.3,'#d7bf9d');s.R(5.2,2.3,1.3,.45,'#ead4b1');s.label(5.85,2.42,'HA-CLOSET-01 back wall');s.frame(2.05,1.32,.48,.55,'KI-ART-02');s.shelf(2.85,1.55,1.0,False);s.R(2.95,1.60,.18,.25,'#dfc5a1',rx=4);s.R(3.2,1.60,.22,.18,'#b17b62',rx=4);s.R(3.48,1.60,.16,.24,'#c1aa79',rx=4);s.label(3.35,1.96,'KI-SHELF-02 mugs / pottery');s.note('Dining table and chairs stand in foreground, leaving doorway clear; closet opens from hall.')
w=Wall('KI-W','Shared living wall, facing west',3.8,3);w.R(.12,0,.7,1.72,'#e9dcb9',rx=12);w.L(.14,.85,.80,.85);w.label(.47,1.85,'KI-FRIDGE-01 side');w.frame(1.20,1.45,.55,.44,'KI-ART-03');w.R(1.85,0,.85,.75,colors['wood']);w.R(1.91,.1,.15,.55,'#9f6c48');w.R(2.49,.1,.15,.55,'#9f6c48');w.label(2.28,.87,'KI-TABLE-01 dining table');w.R(2.05,.15,.40,.65,'#b8785d',rx=5);w.label(2.28,1.04,'KI-CHAIR-01 ×2 at table ends');w.R(2.10,.75,.30,.13,'#d7b26f',rx=9);w.label(2.28,1.20,'KI-BOWL-01 fruit');w.note('Table and chairs are central in plan; elevation is a projected foreground view.')
svg('02-kitchen-elevations.svg',[n,e,s,w],'Kitchen: KI-TILE-01 checker floor, backsplash and plaster wear; KI-PANS-01 and KI-KETTLE-01 enrich the range wall.')
# hall north 12m
n=Wall('HA-N','Living and kitchen entries / entry closet',12,0);n.door(4.05,.9,'LV-DR-01');n.door(6.2,.9,'KI-DR-01');n.R(10.7,0,1.3,2.30,'#d6c1a1');n.R(10.9,.04,.45,2.16,'#e2d1b1');n.R(11.35,.04,.45,2.16,'#e8d9bc');n.L(11.35,.08,11.35,2.18);n.label(11.35,2.43,'HA-CLOSET-01 sliding');n.frame(.45,1.30,.55,.48,'HA-ART-01');n.frame(1.2,1.48,.38,.42,'HA-ART-02');n.R(2.0,0,1.05,.72,colors['wood']);n.R(2.05,.38,.95,.24,'#a57556');n.label(2.52,.84,'HA-CONSOLE-01');n.R(2.2,.73,.24,.26,'#d0b184',rx=5);n.label(2.31,1.13,'HA-VASE-01');n.frame(7.85,1.25,.65,.52,'HA-ART-03');n.frame(8.68,1.42,.45,.43,'HA-ART-04');n.R(9.45,1.5,.72,.05,colors['wood']);
for x in [9.52,9.70,9.88,10.06]:n.C(x,1.44,.022,'#a57a4e');
n.label(9.82,1.68,'HA-HOOKS-01');n.R(3.26,1.86,.08,.20,'#b38b5d',rx=3);n.C(3.30,1.83,.07,'#eed18e');n.label(3.30,2.15,'HA-SCONCE-01');n.R(7.46,1.86,.08,.20,'#b38b5d',rx=3);n.C(7.50,1.83,.07,'#eed18e');n.label(7.5,2.15,'HA-SCONCE-02');n.note('Shallow console max 0.25 m deep; opposing hall pedestal max 0.25 m: 1.18 m clear before trim.')
e=Wall('HA-E','Entry door, facing east',1.8,1);e.door(.175,.9,'HA-ENTRY-01');e.R(1.24,0,.38,.42,colors['wood']);e.label(1.43,.54,'HA-SHOES-01');e.note('Entry opens outward as drawn; verify external landing and code requirements.')
s=Wall('HA-S','Bedroom, bath and office entries',12,2);s.door(3.15,.9,'BR-DR-01');s.door(6.35,.9,'BA-DR-01');s.door(9.65,.9,'OF-DR-01');s.frame(.55,1.35,.48,.52,'HA-ART-05');s.frame(1.25,1.46,.40,.42,'HA-ART-06');s.R(2.05,0,.45,.48,colors['wood']);s.plant(2.16,.48);s.label(2.28,1.2,'HA-PLANT-01');s.frame(4.65,1.32,.55,.52,'HA-ART-07');s.R(7.72,1.65,.65,.05,colors['wood']);s.R(7.83,1.70,.18,.22,'#ba9272',rx=4);s.R(8.08,1.70,.17,.29,'#d8c49c',rx=4);s.label(8.05,2.12,'HA-SHELF-01 vase');s.frame(8.68,1.4,.50,.52,'HA-ART-08');s.R(11.08,0,.62,.45,colors['wood']);s.label(11.39,.57,'HA-BENCH-01 shallow');s.note('All doors swing into rooms; hall plant pedestal and bench max 0.25 m deep.')
w=Wall('HA-W','Gallery focal end, facing west',1.8,3);w.frame(.44,1.28,.9,.65,'HA-ART-09 focal landscape');w.R(.38,0,1.02,.72,colors['wood']);w.R(.45,.11,.88,.42,'#ab7955');w.label(.89,.84,'HA-CABINET-01 shallow');w.R(.73,.74,.22,.27,'#cba985',rx=5);w.label(.84,1.14,'HA-VASE-02 flowers');w.note('Visual terminus: shallow focal cabinet projects max 0.25 m into corridor.')
svg('03-hall-elevations.svg',[n,e,s,w],'Hall: HA-RUNNER-01 runner and HA-CEILING-01 warm fixtures connect the gallery; shallow pieces require clearance check.')
# Replace URL tile with SVG pattern definition in kitchen.
p=out/'02-kitchen-elevations.svg';q=p.read_text();q=q.replace('<g font-family="Arial, sans-serif">','<defs><pattern id="tile" width="26" height="26" patternUnits="userSpaceOnUse"><rect width="26" height="26" fill="#d9b697"/><path d="M0 0H26V26H0Z" fill="none" stroke="#b78f75" stroke-width="1"/></pattern></defs><g font-family="Arial, sans-serif">');p.write_text(q)
