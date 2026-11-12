"""Build a standalone, asset-embedded UI exploration; does not modify game assets."""
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[3]
ATTACH = Path('/Users/davidwallin/.t3/userdata/attachments')

def data(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()

template = Path(__file__).with_name('concept.template.html').read_text()
assets = {
    'MENU_IMAGE': (ATTACH / 'b0806708-59a3-49a6-86a6-d40b82cf6d24-e3a5ced7-bb89-4323-9da9-07ad989a9288.png', 'image/png'),
    'DIALOGUE_IMAGE': (ATTACH / 'b0806708-59a3-49a6-86a6-d40b82cf6d24-21896446-0e1c-440a-b608-761f803fd955.png', 'image/png'),
    'LOGO_IMAGE': (ROOT / 'Art Source/Logo/Asset 4.svg', 'image/svg+xml'),
    'PORTRAIT_IMAGE': (ROOT / 'Art Source/Portraits/T_Portrait_Lukey.png', 'image/png'),
}
for key, (path, mime) in assets.items():
    template = template.replace('{{' + key + '}}', data(path, mime))
Path(__file__).with_name('concept.html').write_text(template)
