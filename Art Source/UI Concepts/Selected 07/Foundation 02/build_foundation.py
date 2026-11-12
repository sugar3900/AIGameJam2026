from pathlib import Path
import base64
import colorsys
import hashlib
import html
import json
import math
import re

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / 'Fonts'
ICON_DIR = ROOT / 'Icons' / 'Phosphor'
COLORS = {'teal': '#1F7384', 'ink': '#11414A', 'cream': '#FFF5E5', 'orange': '#FF7900', 'pink': '#D9005C', 'white': '#FFFFFF', 'friendship': '#76CADB', 'disabledSurface': '#E1E1DE', 'disabledInk': '#565C60'}
C = COLORS
ANGLE = 12

def grid_point(origin, u, v):
    return (origin[0] + u - v * math.tan(math.radians(ANGLE)), origin[1] + v)

def grid_plate(origin, u, v, width, height, fill, outline=None):
    x,y = grid_point(origin,u,v)
    inset = height * math.tan(math.radians(ANGLE))
    return plate(x-inset,y,width+inset,height,fill,outline)

def grid_text(origin, u, v, value, size=26, fill=None, face='body', weight=400, extra=''):
    x,y = grid_point(origin,u,v)
    return text(x,y,value,size,fill,face,weight,extra)

def text(x, y, value, size=26, fill=None, face='body', weight=400, extra=''):
    family = 'Barlow Condensed' if face == 'display' else 'Barlow'
    style = 'italic' if face == 'display' else 'normal'
    weight = 800 if face == 'display' else weight
    if face == 'display' and ANGLE != 7:
        added = math.degrees(math.atan(math.tan(math.radians(ANGLE)) - math.tan(math.radians(7))))
        extra += f' transform="translate(0,{y}) skewX({-added}) translate(0,{-y})"'
    return f'<text x="{x}" y="{y}" fill="{fill or C["ink"]}" font-family="{family}" font-size="{size}" font-weight="{weight}" font-style="{style}" {extra}>{html.escape(value)}</text>'

def rect(x, y, w, h, fill, radius=0, stroke='none', sw=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def plate(x, y, w, h, fill, outline=None, shadow=True):
    # One shared angle, rounded geometry and asymmetric lower/right depth.
    d = h * math.tan(math.radians(ANGLE))
    points = [(x+d,y), (x+w,y), (x+w-d,y+h), (x,y+h)]
    radius = 22 if h > 150 else 12
    corners = []
    for i, v in enumerate(points):
        before, after = points[(i-1)%4], points[(i+1)%4]
        def toward(p):
            length = math.hypot(p[0]-v[0],p[1]-v[1])
            step = min(radius,length/3)
            return (v[0]+(p[0]-v[0])*step/length,v[1]+(p[1]-v[1])*step/length)
        corners.append((toward(before),v,toward(after)))
    pth = f'M{corners[0][0][0]},{corners[0][0][1]}'
    for i,(before,v,after) in enumerate(corners):
        if i: pth += f'L{before[0]},{before[1]}'
        pth += f'Q{v[0]},{v[1]} {after[0]},{after[1]}'
    pth += 'Z'
    edge = outline or C['orange']
    backing = C['orange'] if fill == C['cream'] else C['ink']
    surface = 'url(#pink-surface)' if fill == C['pink'] else 'url(#teal-surface)' if fill == C['teal'] else fill
    layers = ''
    if shadow:
        layers += f'<path d="{pth}" fill="{C["ink"]}" transform="translate(9,12)"/>'
        layers += f'<path d="{pth}" fill="{backing}" stroke="{backing}" stroke-width="4" transform="translate(4,7)"/>'
    return layers + f'<path d="{pth}" fill="{surface}" stroke="{edge}" stroke-width="3"/>'

def icon(name, x, y, size=36, color=None):
    raw = (ICON_DIR / (name + '-bold.svg')).read_text()
    inner = re.sub(r'^.*?<svg[^>]*>', '', raw, flags=re.S)
    inner = re.sub(r'</svg>\s*$', '', inner)
    return f'<g transform="translate({x},{y}) scale({size/256})" fill="{color or C["ink"]}">{inner}</g>'

def line(x1, y1, x2, y2, color=None, width=2):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color or C["friendship"]}" stroke-width="{width}"/>'

def circle(x, y, r, fill='none', stroke=None, sw=2):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="{sw}"/>'

def sheet(parts, filename, height, title):
    style = '''<style>text{font-kerning:normal} @font-face{font-family:'Barlow Condensed';font-weight:800;font-style:italic;src:url('Fonts/BarlowCondensed-ExtraBoldItalic.ttf')} @font-face{font-family:'Barlow';font-weight:400;src:url('Fonts/Barlow-Regular.ttf')} @font-face{font-family:'Barlow';font-weight:600;src:url('Fonts/Barlow-SemiBold.ttf')}</style>'''
    defs = '<defs><linearGradient id="pink-surface" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E80C70"/><stop offset="1" stop-color="#C90055"/></linearGradient><linearGradient id="teal-surface" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#287F91"/><stop offset="1" stop-color="#1A697A"/></linearGradient></defs>'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}" role="img"><title>{title}</title>{style}{defs}' + ''.join(parts) + '</svg>'
    (ROOT / filename).write_text(svg)

def surface_study():
    global ANGLE
    selected_angle = ANGLE
    p = [rect(0,0,1440,1370,C['cream']), text(44,46,'I CAN FIX HIM / ROUNDED SURFACES + SLANT STUDY',23,C['teal'],weight=600),text(44,116,'Same construction. Four angles.',64,face='display'),text(44,162,'Rounded corners, asymmetric border depth and restrained gradients stay identical across options.',25)]
    for i, angle in enumerate([7,10,12,15]):
        ANGLE = angle
        x = 44 + (i%2)*700
        y = 217 + (i//2)*500
        p += [text(x,y,f'{angle}°',46,face='display'),text(x+103,y,'Native italic' if angle==7 else f'Added synthetic slant to match {angle}°',23)]
        p += [plate(x,y+28,640,365,C['cream']),plate(x+45,y+46,550,68,C['teal'],C['white']),text(x+115,y+97,'END THE DAY?',40,C['white'],face='display')]
        p += [text(x+81,y+163,'The day ends and a week will pass.',25),plate(x+76,y+199,480,64,C['pink'],C['white']),icon('play',x+98,y+218,27,C['white']),text(x+250,y+245,'End Day',38,C['white'],face='display'),plate(x+68,y+288,480,64,C['cream']),text(x+249,y+334,'Cancel',38,face='display')]
        p += [text(x,y+443,'Borders: thinner top/left, heavier bottom/right.',22)]
    ANGLE = selected_angle
    p += [text(44,1252,'Barlow’s native italic is 7°. Steeper display samples are sheared; body copy and icons stay upright.',25),text(44,1295,'Gradient: pink #E80C70 → #C90055 / teal #287F91 → #1A697A. Cream reading areas stay flat.',24),text(44,1338,'12° selected for the component shapes, placement grid and display-lettering treatment.',24)]
    sheet(p,'rounded-surface-slant-study.svg',1370,'Rounded popups and buttons compared at 7, 10, 12 and 15 degrees using matched display text')

def placement_grid():
    origin = (330,260)
    for guides in [False,True]:
        p = [rect(0,0,1440,1030,C['cream']),text(44,46,'I CAN FIX HIM / SELECTED 12° / SHARED PLACEMENT GRID',23,C['teal'],weight=600),text(44,116,'The layout follows the same lean.',64,face='display'),text(44,162,'Slanted columns align panels, headers, controls, icons and text-block anchors. Rows stay horizontal.',25)]
        p += [grid_plate(origin,0,0,900,560,C['cream']),grid_plate(origin,40,24,820,84,C['teal'],C['white'])]
        p += [grid_text(origin,96,83,'END THE DAY?',48,C['white'],face='display'),grid_text(origin,64,164,'The day ends and a week will pass.',30)]
        p += [grid_plate(origin,64,230,750,80,C['pink'],C['white']),grid_plate(origin,64,350,750,80,C['cream'])]
        ix,iy = grid_point(origin,90,254)
        p += [icon('play',ix,iy,32,C['white']),grid_text(origin,439,287,'End Day',44,C['white'],face='display',extra='text-anchor="middle"'),grid_text(origin,439,407,'Cancel',44,face='display',extra='text-anchor="middle"')]
        p += [grid_text(origin,64,500,'Body copy and icons remain upright.',25)]
        if guides:
            for u in [0,40,64,439,814,860,900]:
                x0,y0=grid_point(origin,u,-20); x1,y1=grid_point(origin,u,580)
                p += [f'<path d="M{x0},{y0}L{x1},{y1}" fill="none" stroke="{C["friendship"]}" stroke-width="1.5" stroke-dasharray="6 7" opacity=".8"/>']
            for v in [0,24,108,164,230,310,350,430,500,560]:
                x0,y0=grid_point(origin,-20,v); x1,y1=grid_point(origin,920,v)
                p += [f'<path d="M{x0},{y0}L{x1},{y1}" fill="none" stroke="{C["friendship"]}" stroke-width="1.5" stroke-dasharray="6 7" opacity=".8"/>']
        p += [text(44,910,'12° COMPONENT EDGES + 12° PLACEMENT COLUMNS',30,C['teal'],face='display'),text(44,957,'Every 100 px downward shifts the same column 21.26 px left. No independently nudged controls.',26),text(44,998,'This is a skewed placement grid, not a rotation of the popup or its text baselines.',25)]
        sheet(p,'selected-placement-grid'+('-guides' if guides else '')+'.svg',1030,'Selected twelve-degree component and placement grid'+(' with alignment guides' if guides else ''))

def foundations():
    p = [rect(0, 0, 1440, 1130, C['cream'])]
    p += [text(44, 46, 'I CAN FIX HIM / SELECTED 07 / FOUNDATION 02', 23, C['teal'], weight=600), text(44, 116, 'Cooler color. One slant. Shared parts.', 64, face='display')]
    palette = [('Background', 'teal'), ('Ink / shadow', 'ink'), ('Reading surface', 'cream'), ('Accent', 'orange'), ('Action / romance', 'pink'), ('Friendship', 'friendship'), ('Light text', 'white'), ('Disabled', 'disabledSurface')]
    for i, (label, key) in enumerate(palette):
        x = 44 + i * 170
        p += [rect(x, 152, 152, 72, C[key], 8, '#11414A33', 1), text(x, 254, label, 21, weight=600), text(x, 279, C[key], 21)]
    p += [text(44, 326, 'BACKGROUND + FRIENDSHIP SHARE HUE 190°', 22, C['teal'], weight=600)]
    p += [rect(44, 346, 424, 120, '#00565B', 8), text(64, 382, 'Previous background', 23, C['white']), text(64, 427, '#00565B', 36, C['white'], face='display')]
    p += [rect(490, 346, 904, 120, C['teal'], 8), text(512, 382, 'Cooler, lighter background', 23, C['white']), text(512, 427, '#1F7384', 36, C['white'], face='display'), rect(1020, 370, 348, 64, C['friendship'], 6), icon('users', 1035, 382, 38), text(1084, 410, 'Friendship', 29, weight=600)]
    p += [line(44, 499, 1394, 499), text(44, 540, 'DISPLAY / BARLOW CONDENSED', 22, C['teal'], weight=600), text(44, 603, 'WELCOME HOME', 64, face='display'), text(44, 639, 'ExtraBold Italic / adjusted to selected 12° lean', 23)]
    p += [text(760, 540, 'BODY / BARLOW', 22, C['teal'], weight=600), text(760, 581, 'Regular for dialogue. Semibold for replies.', 28), text(760, 620, 'It’s not personal. Everything I own is riding', 27, weight=600), text(760, 654, 'on this flip. If it fails, I lose it all.', 27, weight=600)]
    p += [line(44, 686, 1394, 686), text(44, 726, 'SLANTED EDGES + PLACEMENT GRID = 12° / HORIZONTAL BASELINES', 22, C['teal'], weight=600)]
    p += [plate(44, 751, 292, 76, C['pink'], C['white']), icon('play', 65, 772, 31, C['white']), text(112, 806, 'Continue', 44, C['white'], face='display')]
    p += [plate(365, 751, 267, 76, C['cream']), text(424, 806, 'Options', 44, face='display')]
    p += [plate(662, 751, 217, 76, C['teal'], C['white']), text(699, 806, 'LUKEY', 44, C['white'], face='display')]
    p += [plate(909, 751, 485, 76, C['cream']), text(946, 800, 'Long replies stay upright and wrap.', 27, weight=600)]
    p += [text(44, 884, 'ICONS / PHOSPHOR BOLD / MIT', 22, C['teal'], weight=600)]
    names = [('heart', 'Romance'), ('users', 'Friendship'), ('lightning', 'Friction'), ('wrench', 'Inspect'), ('house', 'Home'), ('door-open', 'Leave'), ('gear', 'Options'), ('play', 'Focus'), ('eye', 'Look'), ('chat-circle-text', 'Talk'), ('check', 'Confirm'), ('info', 'Info')]
    for i, (name, label) in enumerate(names):
        x = 44 + i * 114
        p += [icon(name, x + 18, 908, 50), text(x + 43, 991, label, 20, extra='text-anchor="middle"')]
    p += [text(44, 1045, 'No construction stripes. No ray flourish. No extra yellow accent.', 27, weight=600), text(44, 1086, 'These are editable vector masters using the actual font files and library SVGs, not generated lettering.', 24)]
    sheet(p, 'foundation-sheet.svg', 1130, 'Foundation revision: cooler palette, Barlow type, selected twelve-degree geometry and Phosphor icons')

def reticle(family, state, cx, cy):
    # Symbols shown enlarged; all have a dark contrast underlay.
    if state == 0:
        return circle(cx, cy, 6, C['white'], C['ink'], 3)
    if state == 5:
        return icon('x-circle', cx - 23, cy - 23, 46, C['white'])
    if family == 0:
        return circle(cx, cy, 19, 'none', C['ink'], 7) + circle(cx, cy, 19, 'none', C['white'], 3) + circle(cx, cy, 5, C['white'], C['ink'], 2)
    if family == 1:
        points = f'{cx},{cy-21} {cx+21},{cy} {cx},{cy+21} {cx-21},{cy}'
        return f'<polygon points="{points}" fill="none" stroke="{C["ink"]}" stroke-width="7" stroke-linejoin="round"/><polygon points="{points}" fill="none" stroke="{C["white"]}" stroke-width="3" stroke-linejoin="round"/>' + circle(cx, cy, 4, C['white'], C['ink'], 2)
    name = ['eye', 'eye', 'chat-circle-text', 'hand-pointing', 'moon'][state]
    return circle(cx, cy, 28, C['ink'], C['white'], 2) + icon(name, cx-19, cy-19, 38, C['white'])

def reticles():
    p = [rect(0, 0, 1440, 1350, C['cream'])]
    p += [text(44, 46, 'I CAN FIX HIM / RETICLE STUDY / WORLD + UI STATES', 23, C['teal'], weight=600), text(44, 116, 'Three families. The same action states.', 64, face='display'), text(44, 158, 'Enlarged symbols for comparison; actual gameplay reticles should remain small.', 26)]
    columns = ['No target', 'Inspect', 'Talk', 'Use / open', 'End day', 'Unavailable*']
    prompts = ['', 'Inspect', 'Talk to Lukey', 'Open cabinet', 'Go to bed', 'Not available*']
    x0 = 322
    for i, label in enumerate(columns):
        p += [text(x0 + i * 178, 220, label, 23, weight=600, extra='text-anchor="middle"')]
    families = [('A / DOT + RING', 'Quiet general purpose'), ('B / DIAMOND', 'Graphic focus shape'), ('C / CONTEXT', 'Icon changes by action')]
    for row, (name, sub) in enumerate(families):
        y = 246 + row * 202
        p += [text(44, y + 56, name, 28, face='display'), text(44, y + 94, sub, 19)]
        for state in range(6):
            cx = x0 + state * 178
            p += [rect(cx - 79, y, 158, 176, C['teal'], 8), reticle(row, state, cx, y+66)]
            if state:
                p += [text(cx, y+143, prompts[state], 19, C['white'], weight=600, extra='text-anchor="middle"')]
    p += [line(44, 873, 1394, 873), text(44, 913, 'ACTIVE SYMBOLS / LIGHT + DARK SURFACES', 25, C['teal'], face='display')]
    for family in range(3):
        x = 44 + family * 460
        p += [rect(x, 936, 210, 92, '#FFFFFF', 5, C['friendship'], 1), rect(x+220, 936, 210, 92, C['ink'], 5)]
        p += [text(x+16, 964, 'ABC'[family], 22, C['ink'], weight=600), text(x+236, 964, 'ABC'[family], 22, C['white'], weight=600)]
        p += [reticle(family, 1, x+110, 982), reticle(family, 1, x+330, 982)]
    p += [text(44, 1097, 'SEPARATE UI CURSORS', 28, C['teal'], face='display')]
    p += [icon('cursor', 46, 1118, 42), text(105, 1149, 'Menus / replies', 26), icon('hand-pointing', 386, 1118, 42), text(445, 1149, 'Clickable topic:', 26), text(625, 1149, 'Bon Jovi', 26, C['pink'], weight=600, extra='text-decoration="underline"'), text(898, 1149, 'World reticle hidden', 26, weight=600)]
    p += [text(44, 1211, '*Unavailable is a proposal. Today, invalid or out-of-range targets return to the idle dot.', 25), text(44, 1253, 'No hold-to-interact meter, progress ring, combat crosshair or romance-coded targeting.', 25), text(44, 1295, 'A keeps the current game’s simplicity; C gives more action information but needs new action metadata.', 25)]
    sheet(p, 'reticle-options.svg', 1350, 'Three reticle families across world interaction and separate UI cursor states')

def selected_reticles():
    out = ROOT / 'Reticles'
    out.mkdir(exist_ok=True)
    def symbol(state, cx, cy):
        fill = 'none' if state in ('default', 'unavailable') else C['ink']
        s = circle(cx, cy, 28, fill, C['ink'], 4) + circle(cx, cy, 28, 'none', C['white'], 2)
        if state == 'default':
            return s + circle(cx, cy, 5, C['white'], C['ink'], 2)
        if state == 'unavailable':
            return s + f'<path d="M{cx-8} {cy-8}l16 16m0 -16l-16 16" fill="none" stroke="{C["ink"]}" stroke-width="6" stroke-linecap="round"/><path d="M{cx-8} {cy-8}l16 16m0 -16l-16 16" fill="none" stroke="{C["white"]}" stroke-width="4" stroke-linecap="round"/>'
        name = {'inspect': 'eye', 'talk': 'chat-circle-text', 'use': 'hand-pointing', 'end-day': 'moon'}[state]
        return s + icon(name, cx-19, cy-19, 38, C['white'])
    states = [('default', 'Default', 'No actionable target'), ('inspect', 'Inspect', 'Inspect'), ('talk', 'Talk', 'Talk to Lukey'), ('use', 'Use / open', 'Open cabinet'), ('end-day', 'End day', 'Go to bed'), ('unavailable', 'Unavailable', 'Reserved / not in use')]
    p = [rect(0, 0, 1440, 770, C['cream']), text(44, 46, 'I CAN FIX HIM / SELECTED RETICLE FAMILY / REVISION 04', 23, C['teal'], weight=600), text(44, 116, 'Context icons. One ring. One radius.', 64, face='display'), text(44, 162, 'Transparent dot-and-ring at rest. The dark center fills only for actionable targets.', 25)]
    for i, (state, label, prompt) in enumerate(states):
        cx = 154 + i*225
        p += [rect(cx-103, 200, 206, 230, C['teal'], 8), text(cx, 242, label, 25, C['white'], weight=600, extra='text-anchor="middle"'), symbol(state, cx, 308), text(cx, 393, prompt, 20, C['white'], extra='text-anchor="middle"')]
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">{symbol(state,32,32)}</svg>'
        (out / (state + '.svg')).write_text(svg)
    p += [text(44, 484, 'SHARED GEOMETRY', 26, C['teal'], face='display'), text(44, 527, '32 px box at 1080p: 14 px ring radius and 1 px light rim, with a thin dark contrast edge.', 27), text(44, 568, 'Shown at 2×. Default has no interior fill; active icons use a dark disk and a shared 19 px icon box.', 25)]
    p += [text(44, 628, 'UNAVAILABLE IS RESERVED', 26, C['teal'], face='display'), text(44, 668, 'Not currently emitted by the game. Use only for a recognizable, explicitly blocked target with a reason.', 25), text(44, 709, 'No target / out of range → default. Menus / dialogue → world reticle hidden; separate UI cursor.', 25)]
    sheet(p, 'selected-reticles.svg', 770, 'Selected reticle family with shared ring radius, contextual icons, and reserved unavailable state')

def update_proposal():
    proposal = ROOT.parent / 'design-system.proposal.json'
    backup = ROOT / 'design-system.previous.json'
    if not backup.exists():
        backup.write_bytes(proposal.read_bytes())
    d = json.loads(proposal.read_text())
    previous_revision = ROOT / 'design-system.revision02.json'
    if not previous_revision.exists():
        previous_revision.write_bytes(proposal.read_bytes())
    d['status'] = 'Revision 06: user selected 12 degrees for slanted component edges, placement-grid columns and display-lettering treatment. Rounded corners, gradients and reticle decisions retained.'
    d['revision'] = 6
    for key, val in C.items():
        if key not in d['colors']:
            d['colors'][key] = {'role': 'Friendship indicator and cool accent'}
        d['colors'][key]['hex'] = val
    d['colors'].pop('mint', None)
    d['colorHue'] = {'teal': 190, 'friendship': 190, 'ink': 190, 'units': 'degrees HSL, rounded RGB hex'}
    d['typography']['display'] = {'family': 'Barlow Condensed', 'weight': 800, 'style': 'Italic', 'file': 'Foundation 02/Fonts/BarlowCondensed-ExtraBoldItalic.ttf', 'license': 'SIL Open Font License 1.1', 'nativeItalicAngleDegrees': -7}
    d['typography']['body'] = {'family': 'Barlow', 'weights': [400, 600], 'style': 'Regular', 'files': ['Foundation 02/Fonts/Barlow-Regular.ttf', 'Foundation 02/Fonts/Barlow-SemiBold.ttf'], 'license': 'SIL Open Font License 1.1'}
    d['geometry']['slantDegrees'] = 12
    d['geometry']['accentPlate'] = 'All slanted elements and placement columns use the same selected 12-degree right lean. Barlow Condensed Italic is given matching additional synthetic shear. Applies to button shapes, tabs, badges, header plates, slanted panels, outlines, focus shapes and shadows; no independent angles.'
    d['geometry']['slantFormula'] = 'For a side edge of height h, top-to-bottom horizontal inset is h * tan(12 degrees). Baselines stay horizontal. Do not rotate panels or shear body text, icons or brand masters.'
    d['geometry']['panel'] = 'Cream reading surface with rounded corners and a consistent slanted side edge; cool-teal header, asymmetrical orange border and short ink shadow. Keep content and baselines horizontal.'
    d['geometry']['borderConstruction'] = {'topAndLeftReferencePixels': 3, 'lowerRightExtrusionOffset': [4, 7], 'inkShadowOffset': [9, 12], 'cornerRounding': {'smallControls': 12, 'largePanels': 22}, 'rule': 'All contour layers share the same slant and rounded path. Values are design reference units, to be verified in Unreal.'}
    d['geometry']['slantStudy'] = {'angles': [7, 10, 12, 15], 'status': 'User selected 12 degrees', 'selectedAngle': 12, 'sheet': 'Foundation 02/rounded-surface-slant-study.svg', 'fontNativeItalicDegrees': 7, 'steeperFontTreatment': 'Synthetic added shear on display glyphs only. Extra shear tangent = tan(target angle) - tan(7 degrees); body text and icons are not sheared.'}
    d['geometry']['placementGrid'] = {'angleDegrees': 12, 'formula': 'x = originX + u - v * tan(12 degrees); y = originY + v', 'scope': ['Panel faces', 'Header plates', 'Button origins', 'Icon anchors', 'Text-block anchors'], 'rows': 'Horizontal', 'bodyAndIcons': 'Upright and unskewed; only their anchors follow the grid', 'sample': 'Foundation 02/selected-placement-grid-guides.svg', 'rule': 'Align controls through shared grid coordinates, not arbitrary per-control horizontal offsets.'}
    d['typography']['display']['effectiveLeanDegrees'] = 12
    d['typography']['display']['addedShearTangent'] = math.tan(math.radians(12)) - math.tan(math.radians(7))
    d['surfaces'] = {'pinkGradient': ['#E80C70', '#C90055'], 'tealGradient': ['#287F91', '#1A697A'], 'direction': 'Vertical, lighter top to darker bottom', 'use': ['Pink action buttons and labels', 'Teal buttons, labels and header plates'], 'flat': ['Cream reading surfaces', 'Disabled controls', 'Reticles'], 'avoid': 'Glossy highlights, bevels and per-screen gradient variations'}
    d['geometry']['shadowOffsetReferencePixels'] = [9, 12]
    d['decorations'] = {'constructionStripes': 'Removed', 'threeRayFlourish': 'Removed from base kit; may be revisited later for surprises, not currently enabled'}
    d['icons'] = {'library': 'Phosphor', 'weight': 'Bold', 'license': 'MIT', 'source': 'https://github.com/phosphor-icons/core', 'directory': 'Foundation 02/Icons/Phosphor', 'rule': 'Use Bold SVGs consistently; no arbitrary weight mixing or skewing icons to match panel edges.'}
    for c in d['components']:
        if c['name'] == 'Icon and accent set':
            c['name'] = 'Icon set'
            c['assets'] = ['Heart', 'Users', 'Lightning', 'Wrench', 'House', 'Door-open', 'Gear', 'Play', 'Check', 'Info', 'Eye', 'Chat-circle-text', 'Hand-pointing', 'Moon', 'X-circle', 'Cursor']
            c['rules'] = ['Use Phosphor Bold consistently, with aligned optical sizes.', 'No construction stripes or ray-flourish graphics.', 'Do not add hearts to reply focus or imply unearned relationship outcomes.']
        elif c['name'] == 'HUD label':
            c['rules'] = ['Consistent corner anchors and safe margins.', 'Selected contextual family with dot-and-ring default: Foundation 02/selected-reticles.svg.', 'World reticle hidden outside Playing; UI cursor is separate.', 'Unavailable-target state is proposed; existing code suppresses invalid targets.']
        elif c['name'] == 'Relationship meter':
            c['variants'] = ['Romance: Phosphor heart, pink', 'Friendship: Phosphor users, cool blue-teal', 'Friction: Phosphor lightning, orange']
        elif c['name'] == 'Panel shell':
            c['rules'] = ['Rounded cream face with consistent slanted edges; shared asymmetrical border layers.', 'Teal header plates use the selected subtle gradient.', 'No rotation of a complete modal; body text stays upright.']
    d['reticles'] = {'status': 'User selected C contextual icons with a transparent A dot-and-ring default. Shared radius/rim; dark fill only on actionable targets. Design assets only, not implemented.', 'family': 'C + A default', 'currentRuntimeStates': ['Idle dot', 'Actionable target plus prompt', 'Hidden outside exploration'], 'actionCategories': ['Inspect', 'Talk', 'Use/open', 'End day'], 'geometryAt1080p': {'boxPixels': 32, 'outerRadiusPixels': 14, 'rimPixels': 1, 'defaultDotRadiusPixels': 2.5, 'contextIconBoxPixels': 19, 'defaultBacking': 'transparent', 'actionableBacking': '#11414A', 'unavailableBacking': 'transparent', 'rimAndIcon': '#FFFFFF'}, 'assets': 'Foundation 02/Reticles', 'sheet': 'Foundation 02/selected-reticles.svg', 'unavailable': {'status': 'Reserved; no runtime usage planned now', 'visual': 'Same radius and rim with transparent interior; white inner X with a thin ink outline matching the default dot, no actionable dark fill', 'useOnlyWhen': 'A recognizable target is deliberately blocked and the UI can give a meaningful reason', 'notFor': ['Empty space', 'Out-of-range target', 'Ordinary uninteractive scenery', 'Brief post-encounter or spawn transition locks', 'A door or bed that still opens a usable confirmation modal'], 'possibleFutureCase': 'An explicit durable interaction lock exposed through semantic target metadata'}, 'uiCursors': ['Arrow for UI selection', 'Hand for clickable topic'], 'implementationRequirement': 'Add explicit semantic action metadata for contextual icons; do not infer action category by parsing localized prompt strings. Keep current input behavior during radio playback separate from world targeting.'}
    d['nextArtifact'] = 'Assemble component masters using the selected palette, fonts, twelve-degree slant and matching placement grid and contextual reticle family; no further reticle family selection needed.'
    proposal.write_text(json.dumps(d, indent=2) + '\n')

def sources():
    rows = []
    for p in sorted(FONT_DIR.glob('*')):
        fam = 'barlowcondensed' if 'Condensed' in p.name or p.name.startswith('barlowcondensed') else 'barlow'
        filename = p.name if p.suffix == '.ttf' else 'OFL.txt'
        rows.append({'file': str(p.relative_to(ROOT)), 'source': f'https://raw.githubusercontent.com/google/fonts/main/ofl/{fam}/{filename}', 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    for p in sorted(ICON_DIR.glob('*')):
        rel = 'LICENSE' if p.name == 'LICENSE' else 'assets/bold/' + p.name
        rows.append({'file': str(p.relative_to(ROOT)), 'source': 'https://raw.githubusercontent.com/phosphor-icons/core/main/' + rel, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT / 'sources.json').write_text(json.dumps(rows, indent=2) + '\n')

if __name__ == '__main__':
    foundations()
    surface_study()
    placement_grid()
    reticles()
    selected_reticles()
    update_proposal()
    sources()
