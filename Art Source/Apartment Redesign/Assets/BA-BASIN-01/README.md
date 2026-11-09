# BA-BASIN-01 · vintage pedestal basin

A separate, modelled ceramic pedestal and hollow curved basin with twin vintage taps, overflow and drain. The chosen [concept and multiview sheet](concepts/basin-v1.png) is the form reference; [ivory-enamel-v2.png](textures/ivory-enamel-v2.png) is an AI-generated color texture used in the Blender material. The surface brushwork is color, not modeled paint relief.

- **Dimensions:** body footprint 0.64 × 0.56 m, overall height including taps approximately 0.95 m. Units are metres, Z up; front faces −Y.
- **Parts:** `BA_BasinBody.fbx` has a floor origin; `BA_BasinTap_L.fbx` and `BA_BasinTap_R.fbx` have pivots on their respective valve axes at (−0.18, 0.185, 0.922) and (0.18, 0.185, 0.922) m. Their FBX object transforms retain those positions relative to the body; translate/convert them consistently on import. Rotate each handle about its local vertical Z axis. Spouts are fixed to the body.
- **Source:** `model/BA-BASIN-01.blend` and `model/build_basin.py`. The material references the adjacent `textures/ivory-enamel-v2.png`; recreate the material in Unreal and verify the relative scale and placement of both pivots.
- **Validation:** `model/validate_fbx.py` reimports all three FBXs and checks finite vertex positions/UVs, presence of UVs, and zero-area triangles; all passed. The three-quarter preview is `previews/basin-three-quarter.png`.
- **Remaining:** Unreal material/UV appearance, collision, tap pivot behavior, and fit under bathroom lighting and mirror have not been tested. The rolled lip and pedestal use a continuous unwrap with the seam at the rear; the appearance still needs contextual review.
