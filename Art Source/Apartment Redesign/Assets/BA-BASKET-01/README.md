# BA-BASKET-01 — wicker towel basket

Status: Blender candidate for visual review; not imported or tested in Unreal. `concepts/wicker-towel-basket-v1.png` is the selected four-view guide. `previews/basket-perspective.png` shows the current model. The first render had floating spiral ends and an overhanging towel; the roll geometry and placement were revised, then the weave was reduced from about 68k to 28k triangles.

## Model and placement

A warm oval wicker basket with two integral handles, plus two ivory and one rose rolled towel. Blender uses metres, Z up, with the shared assembly origin at floor-centre and the towel roll ends facing -Y. The basket FBX is **0.466 × 0.342 × 0.225 m**, within the nominal 0.50 × 0.40 m floor footprint. Individual towels are approximately 0.136 × 0.184 × 0.142 m. Place all exports at the same transform to reproduce the preview:

- `model/BA_Basket.fbx`: wicker base, interlaced stakes/weft, rim and handles.
- `model/BA_Towel_0.fbx`, `BA_Towel_1.fbx`, `BA_Towel_2.fbx`: independent rolled towel meshes, with geometry for folded ends and hems. They can be repositioned individually; this is not an authored animation.
- `model/BA-BASKET-01.blend` and `model/build_basket.py`: editable master and reproducible generator. Textures are referenced relatively.

## Materials and limitations

`textures/wicker.png` and `textures/terry.png` are independently generated painted color textures based on the concept. The basket uses two color variants of wicker; the ivory and rose towels use the same terry texture with different tint multipliers. Blender color-node multipliers and roughness do not transfer reliably through FBX: recreate them in Unreal and tune against the room lighting. The modeled spiral edges are deliberately stylized and need visual assessment at game camera distance.

The basket is **27,616 triangles**, each towel **2,620 triangles** (35,476 total). This is still relatively heavy for a small prop because the weave is modeled; consider LODs or baking if the scene's performance budget requires it. No custom Unreal collision is provided: use a simple oval/box collision for the basket and consider leaving the decorative towels nonblocking. Inspect interlaced reeds, texture scale, contact shadows and placement on the bathroom floor in Unreal; none has been tested there.

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_basket.py` to rebuild and `... -b --python model/validate_fbx.py` to reimport each FBX. The current round trip passed finite geometry/UV, nonzero triangle and basket-footprint checks; counts and dimensions are in `model/validation.txt`. These checks do not establish Unreal import, collision or in-room appearance.

## Optional lower-detail basket

`model/BA_Basket_LOD1.fbx` is a separate lower-detail basket body; it does not replace `BA_Basket.fbx` or change the three towel exports. `model/BA-BASKET-LOD1.blend` and `model/build_basket_lod1.py` are its editable source and generator. In `previews/basket-lod-comparison.png`, the reviewed original is on the left and the lower-detail candidate is on the right; both have identical framing and the same towel meshes. The coarse weave has fewer, thicker courses, so the difference remains visible up close.

LOD1 has **15,456 triangles** versus 27,616 for the basket alone, a **44% reduction**. Including the three unchanged towels, the assembly is 23,316 triangles versus 35,476 (34% reduction). Reimport checks in `validation-lod.txt` found finite geometry, UVs and nonzero triangles; `validation-lod-compatibility.txt` verifies that the original and LOD1 have the same origin and material-slot names. Bounds match at 0.466 × 0.342 × 0.225 m. Both use `wicker.png` and the same two color-multiplied wicker materials, but their UV islands differ, so the exact texture pattern can shift at the transition.

In Unreal, import the LOD1 FBX as the basket static mesh's LOD 1 and map its two material slots to the same materials as LOD 0; keep the towels as separate meshes. Choose the switching screen size in the actual bathroom and test from the player camera for a visible change in weave, texture or shadows. A further low-poly baked version may be needed for a distant LOD or tighter budgets. No Unreal import or transition has been tested.
