# BR-DRESSER-01

Shallow 1950s walnut dresser with arched mirror, three independent sliding drawers, brass cup pulls and painted wood base color. The selected concept and five-view sheet are in `concepts/` and `references/`. `textures/walnut-painted-v2.png` is an AI-generated painterly base-color reference used in the Blender material.

- Closed outer footprint: 1.15 m × 0.40 m; top height 0.925 m; mirror top approximately 1.615 m. Axes: width X, depth Y, up Z; front is −Y.
- `BR_Dresser_body.fbx`, three `BR_Dresser_drawerN.fbx` and `BR_Dresser_mirror.fbx` share a floor-centered origin. Assemble at the same transform; translate each drawer on local −Y. The preview opens the middle drawer by 0.22 m. Drawer clearance and player collision must be tested when open.
- Rebuild with `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'model/build_dresser.py'` from this asset directory. Test FBX round-trip with the same command and `model/validate_fbx.py`.
- All five FBXs reimport with finite vertices and UVs, no zero-area faces and UVs present. `previews/dresser-closed.png` and `dresser-open.png` show both states. Mirror is a simple reflective material and must be configured/tested in Unreal.

The render is an asset preview. Actual Unreal material assignment, texture orientation, pivots and cabinet/drawer collision remain untested in the apartment scene.

Revision: arched glass and frame joints adjusted, drawer gaps narrowed and wood grain oriented along each drawer; distinct UV offsets and a second painted texture add varied wear.
