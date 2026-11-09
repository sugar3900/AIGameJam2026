# Apartment redesign: design brief

## Visual target

The selected reference is [painterly fixer-upper](../../../Art%20Source/Environment%20Concepts/painterly-fixer-upper.png). Preserve its inviting mid-century character, useful original trim, vintage furniture, warm light, floral fabrics, sage cabinetry, old enamel, pink bathroom tile and carefully located problems. Make the art look painted through color and brushwork; do not model every surface as heavy physical paint. A good apartment with tangible work to do, not a ruin or a newly renovated showroom.

## Layout criteria

Design independently of the previous four rectangles. Include a proper entry and hallway, usable closets and a small second bedroom or office. Every room should have purposeful sightlines and objects of interest in several directions. Windows must face outside; doors must have feasible openings and swings; circulation, access to furniture, and interaction space must be shown. Dimension in metres and give each wall and item a stable ID, so plans, elevations and assets can be cross-checked.

## Production gates

1. Compare five materially different plans for spatial character, believable circulation, light, gameplay readability and buildability. Record the choice and tradeoffs.
2. Draw every wall of each room with openings, furniture, small objects and specific repair conditions. Check elevations against the chosen scaled plan before locking the inventory.
3. For each unique item record dimensions, materials, wall/room placement, reuse and animation/repair states. Generate and select item concepts; for moving or repaired items include before/after states. Reference sheets are visual guides: reconcile inconsistent AI views against the approved dimensions and elevations.
4. Store each asset's selected concept, alternatives, multi-view references, source model, exports, textures and review renders under its stable ID. In Blender use metres, Z up, floor origins and separate pivoted moving parts. When a generated texture is far from the target, generate several genuinely different candidates from scratch and compare or combine their strengths; use incremental edits for near matches. Review shape, texture and color against the selected concept and reference image; check finite geometry, UVs, normals, degenerate faces and FBX round trip.
5. Build the shell from the selected plan and elevations. Check the whole apartment composition with the props before importing. In Unreal check materials in context, saved/reloaded assets, navigation, line traces, animation, repair/save/reset, character placement, dialogue framing and lighting.

## Game integration constraints

Preserve malady IDs: Wyatt/fuse in living room, Lukey/leak in kitchen, Tyler/cracked tile in bathroom and Malcolm/mold on the bedroom closet interior, revealed by opening its doors. Existing room IDs, save data and floor-plan travel need explicit migration and testing when coordinates change. `AFixHimRoom` currently supplies both overlap bounds and map rectangles; hallway and office need deliberate room and UI treatment. Keep entry locations and old saves clear of walls, and validate doorways with the player capsule. Preserve animated pivots, authored materials, repair-damage attachment tags and visibility traces. Dialogue cameras and character positions need checking in the finished layout, not just in an empty shell.

## Bedroom repair direction

White wood wainscoting gives the bedroom its original character. Its localized flaking lead paint is a separate inhabitant/repair location; design intact and deteriorated appearances and determine how it connects to gameplay. Black mold belongs on the back wall inside the bedroom closet, not on the bedroom walls. The closet is large enough for a man to stand inside and contains a single bare hanging bulb. The player opens the hinged closet doors to reveal and interact with Malcolm; keep a clear line of sight and preserve the repaired state. See `elevations/bedroom-closet-interior.svg`.

### Closet reveal acceptance

- Closet interior: nominal 1.80 × 1.45 m, 2.75 m ceiling; preserve standing room for Malcolm and a single exposed hanging bulb. The doorway has two outward-hinged leaves.
- Before opening: doors conceal the mold and Malcolm. Opening them reveals the dark mold on the interior back wall and allows the interaction to be reached; repair removes the mold but leaves the closet, bulb and doors intact.
- Stage the actual character, capsule and dialogue camera in the constructed closet. Verify the door leaves, shelf geometry, trace targets and save/reload/repaired/reset states together; the 2D drawing alone cannot prove this works.
- Bedroom white wainscoting is the separate lead-paint hunk location, currently a backlog character in the game design document. Its old and repaired appearances and new inhabitant/interaction flow must be designed without silently changing the four existing IDs or save semantics.
