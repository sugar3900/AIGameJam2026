# KI-TABLE-02 — FIX-035 apron UV correction

UV-only replacement of KI-TABLE-01/model/KI_TABLE_01.fbx. Every geometry face and all non-apron UVs are preserved (fresh FBX comparison at 1 micrometre). Same floor origin, scale, dimensions and source axes. No new collision geometry or gameplay.

The four apron boards now use a continuous position-based projection per board: grain runs along the board length, with the same density on long and short boards. U = (length_coordinate + 1.5) / 3.0; V = (Z - .60) / 1.7 + .45. This uses the tabletop's source 3.0 m-per-U grain density (scales with the installed actor). The mid-rail UV-island break is removed. Tiny bevel edges follow the board projection; seams remain at physical board joins only.

## Integration

- Replace the existing table static mesh with models/KI_TABLE_02.fbx at the exact current transform; retain the existing installed collision settings/body setup. Do not add another table actor or change chairs, dressing, top or legs.
- Preserve all existing material assignments by slot name. `Table_Sage_Painted` retains its legacy name for reliable mapping, but now means the WOOD apron.
- IMPORTANT: use the table top's existing wood texture/finish on that slot with IDENTITY UV0. Remove the interim U/V swap and 1.5 / .215 rescaling from MI_Table_ApronWood for this mesh. Applying it again would rotate/distort the newly corrected UVs.
- The copied table-wood-v2.png is the exact original source image. No colour rebake; keep the engine's installed tint and roughness.
- Table_Wood_Painted top/legs and Table_Edge_Wear remain unchanged. No old-source files are overwritten.

`build_uv.py` imports the original FBX, changes only apron UVs, exports and imports the result again, then validates canonical face geometry and all other UVs. `validation.json` reports four continuous board mappings and fresh-export preservation. Source preview shows a long and end rail. Confirm installed close/corner views, retained collision and route before closing FIX-035.
