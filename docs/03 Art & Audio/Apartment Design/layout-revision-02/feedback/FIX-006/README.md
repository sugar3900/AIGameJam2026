# FIX-006 — unique apartment wall-art collection

Seventeen original wall-art instances now have seventeen distinct generated paintings and individually modeled frame treatments. The full source contact sheet is approved and FBXs are roundtrip validated; placement, materials and lighting still require the engine owner’s review. Existing artwork exports remain untouched.

[Review contact sheet](<../../../../../../Art Source/Apartment Redesign/Assets/ART-REV02-COLLECTION/previews/contact-sheet.png>) · [Authoritative instance inventory](wall-art-inventory.json)

## Priority hall painting

`HA-ART-02:058` becomes `ART-REV02-006`, **The orchard gate**: a 1.30 × 0.90 m landscape in a 5.5 cm deep aged gilt ogee frame with walnut outer edge and restrained leaf corners. Its center is plan X 5.15 m, back plane Y 5.54 m, bottom Z 1.12 m; the forward face is Y 5.485 m. This leaves 39 cm to each neighboring doorway casing. The other sixteen instances preserve their approved outer width/height and 3.5 cm depth.

## Instance handoff

| Existing instance | New source asset | Painting | Frame |
| --- | --- | --- | --- |
| `LV-ART-04:040` | `ART-REV02-001` | Tidal inlet at blue hour | Walnut cove, narrow chalk liner |
| `HA-ART-02:041` | `ART-REV02-002` | The reader in sage | Ebonized step frame, muted gold inner bead |
| `LV-ART-04:045` | `ART-REV02-003` | White horse in the meadow | Honey oak bevel with broad flax mount |
| `HA-ART-09:056` | `ART-REV02-004` | Footbridge after the rain | Mahogany scoop, brass bead and small corner rosettes |
| `HA-ART-03:057` | `ART-REV02-005` | Courtyard laundry | Umber stepped rail, blue-grey inner slip |
| `HA-ART-02:058` | `ART-REV02-006` | The orchard gate | Broad aged gilt ogee with walnut outer edge and leaf corners |
| `HA-ART-02:060` | `ART-REV02-007` | Swallows and hawthorn | Ebony half-round with ivory mount and pencil fillet |
| `HA-ART-03:061` | `ART-REV02-008` | Boats at low tide | Weathered teal scotia with bleached wood slip |
| `BR-ART-FLORAL-01:062` | `ART-REV02-009` | Rose stems and a bee | Ivory bead-and-reel, thin rosewood inner edge |
| `BR-ART-FLORAL-01:064` | `ART-REV02-010` | Unfurling woodland fern | Pale oak flat frame, double ivory/sage mount |
| `BR-ART-FLORAL-01:066` | `ART-REV02-011` | Anemones in the blue jug | Oxblood convex lacquer and fine gold fillet |
| `BR-ART-FLORAL-01:067` | `ART-REV02-012` | Magnolia at dusk | Oval walnut bolection with cream oval liner |
| `OF-ART-LANDSCAPE-01:070` | `ART-REV02-013` | Hillside farm in spring | Dark oak sloping rail with warm paper mount |
| `OF-ART-BOTANICAL-01:071` | `ART-REV02-014` | Woodland mushroom study | Slim antique brass double-round, terracotta mount edge |
| `OF-ART-BOTANICAL-01:073` | `ART-REV02-015` | Moths in the fern garden | Olive fluted wood with natural oak edge |
| `BA-ART-01:081` | `ART-REV02-016` | Lavender and sage | Chalk cream beaded pine with blue-grey mount |
| `KI-ART-01:082` | `ART-REV02-017` | Pears by the coffee pot | Dark farmhouse walnut, chamfered edge and brass corner pins |

## Integration

Each asset folder contains a packed Blender scene, a single visual FBX mesh plus a named UCX box, artwork and baked frame-color maps, a source preview, README and machine-readable manifest. `ART-REV02-COLLECTION/build-manifest.json` collects all seventeen manifests, including wall-datum positions and proposed engine yaw.

The source origin is the bottom-center of the rear wall plane, with front −Y and Z up, in metres. Use the manifest placement rather than retaining an old mesh’s pivot compensation. Importing keeps source X and flips Y: north-facing artwork uses yaw180, south0, east−90 and west90. Verify the visible face against the wall at import. Source scale is1. All original instance labels remain stable for reconciliation.

Artwork PNGs are original generated files, each distinct by SHA256. Their UVs crop at equal pixel scale to fit each aperture; images are never stretched. The oval magnolia frame keeps the main flowers and moon visible. Wood/paint colors are baked to `T_Frame_BaseColor.png` in native Blender; use it directly as sRGB. Gilt/mount/slip constants are documented per asset; opaque rough painting surfaces avoid distracting glass glare.

Use legacy FBX for UCX, or disable collision on wall dressing when the wall already provides it. These assets have no new interactions or RepairDamage tags. Do not delete the original source folders. Reconcile all seventeen records against the actual map, then inspect them under the apartment lighting.

## Reproduction and checks

Run `ART-REV02-COLLECTION/build_collection.py`, then `finalize_collection.py`, with headless Blender and two threads. Builders write only the new collection folders and this FIX006 inventory. Original generated artwork textures are read-only inputs. The finalizer bakes portable frame maps, reimports every FBX and assembles the labeled contact sheet in a native Blender scene.

`ART-REV02-COLLECTION/validation.json` verifies17unique artwork hashes,17single visual meshes,17UCX boxes, preserved UVs, bounds, zero source origins and unchanged generated image files. Source acceptance does not substitute for the engine lighting/placement review.

The collection manifest includes exact material-slot contracts. A `base_color_texture` replaces the fallback constant rather than multiplying it. Numeric roughness/metallic and mount/slip colors are recorded per slot.
