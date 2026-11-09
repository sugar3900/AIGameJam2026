# KI-RANGE-FLAME-01 — independently switchable gas flame

**Status: provisional Blender art handoff; not yet imported or tested in Unreal.** A short ring of twelve stylized blue gas jets fits one modeled burner on `KI-RANGE-01`. The existing range body and burner stay visible in both states. **Off:** hide the separate flame mesh and turn off its light/emission. **On:** show it and enable the emissive material and optional light. The range mesh and gameplay interaction are not modified by this asset.

## Files

- `concepts/burner-on-off.png`: generated off/on visual target based on the painterly fixer-upper and existing range.
- `model/KI_Range_Flame.fbx`: one burner flame mesh with the `Flame_Outer_Blue` material slot and `FlameTint` vertex color/alpha; no range or preview light is exported.
- `model/KI-RANGE-FLAME-01.blend`: editable source with preview range and lights. The stove is preview-only; it imports the existing `KI-RANGE-01` body and references its enamel texture.
- `previews/burner-off.png`, `burner-on.png`, `burner-detail-off.png`, `burner-detail-on.png`: actual Blender range shown with the front-left flame hidden/visible. The apparent blue bounce uses a Blender preview point light, not exported geometry.
- `model/build_flame.py`, `model/validate_flame.py`, `model/validate_uv.py`: reproducible build and reimport checks. Run with `/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python <script>` from the project root. Texture bitmaps are not required: per-vertex `FlameTint` RGB transitions gently from blue/cyan at the base toward blue at the tip, while its alpha fades toward both ends. Keep vertex colors when importing.

## Placement and orientation

Blender coordinates use **metres, X across stove, Y depth, Z up and stove front −Y**. The standalone FBX origin is the **centre of one burner at gas-port height**, not the range floor. Export options are `axis_forward=-Y`, `axis_up=Z`, with unit scaling; verify Unreal's import transform and actual body pivot before using the offsets. The twelve existing gas ports are on a **0.046 m radius** around the burner centre.

Relative to the `KI_RANGE_Body.fbx` floor-centre origin, place instances at these Blender metre coordinates:

| Burner | X | Y | Z |
|---|---:|---:|---:|
| Front left | −0.18 | −0.15 | 0.931 |
| Front right | +0.18 | −0.15 | 0.931 |
| Back left | −0.18 | +0.15 | 0.931 |
| Back right | +0.18 | +0.15 | 0.931 |

The range body positions and gas-port elevations come from `KI-RANGE-01/model/build_range.py`. Mesh bounds relative to burner origin are approximately **0.103 × 0.103 × 0.030 m**; short jets beneath the four grate spokes reduce visible intersections. Use one instance for a single switchable burner or four separately switchable instances if required. Check actual cooktop alignment, grates, cookware, material sorting and visibility from the real camera; FBX axis conversion or an already-rotated range can change the required relative transform.

## Unreal material and interaction

Recreate one translucent/unlit emissive material driven by the FBX **`FlameTint` vertex color**. Use RGB for a soft blue/cyan emissive tint and vertex alpha multiplied by an opacity scalar (the Blender preview uses 0.38); preserve vertex colors on import. The Blender preview emission strength is 0.8, an artistic reference rather than a calibrated Unreal value. Adjust intensity and opacity under actual game exposure; inspect both the mesh and sorting from gameplay distance. The revised effect has one surface layer per flame jet and no inner overlay, reducing translucency overdraw; it has no baked halo. FBX does not transfer the complete Blender shader graph.

An emissive mesh alone does not necessarily illuminate surrounding surfaces: attach a small blue point light at the burner and switch it together with visibility if desired, then tune in-scene. Disable collision, shadow casting and navigation impact for the flame effect. No flame animation, light, particle effect, control code, or UE material is authored in the FBX. Avoid an emissive halo that persists in the off state.

`model/validation.log` records a fresh Blender FBX reimport: **1 mesh, 2,592 triangles, finite positions and UVs, no degenerate geometry, burner-centre origin, and preserved vertex-color alpha range ~0.024–0.996**. `validate_uv.py` also found zero degenerate UV triangles for the mesh. These checks do not verify Unreal's axis conversion, material opacity, light behavior or the actual in-game interaction.
