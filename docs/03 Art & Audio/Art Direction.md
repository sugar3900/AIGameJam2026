---
tags: [art]
status: in progress
---
# Art Direction

## Environment style

An old, lived-in apartment with warmth and personality, but substantial visible repairs still to make. Use vintage appliances, patterned fabrics, aged wood, pink bathroom tile and a restrained, warm palette. The painterly quality belongs to the visual treatment: shapes, color and brushwork should feel illustrated, rather than making the apartment look as though it has been covered in thick paint.

## Character rendering

Keep the characters integrated with each room's actual light colour, indirect light, shadows and exposure. Stylization should simplify their material response (normal detail, gloss and metallic reflections), rather than replace scene lighting with unlit colour or a camera-relative key. Compare changes in each character's encounter location: Tyler in the bathroom, Lukey in the kitchen, Wyatt in the living room, and Malcolm in the bedroom closet with its doors open. Lead Paint is intended for the office but has no gameplay integration yet; office model previews must be labeled as staged. Lead Paint is separate from Az, the backlog asbestos character.

The selected matte material retains real scene lighting while suppressing fine normal detail, gloss and metallic reflections. The illustrated alternative retains a little more surface response. Neither is cel shading; true cel shading would need deliberate shadow bands. Keep the original material available as the comparison baseline.

## Guiding concepts

These AI-generated explorations are visual targets, not screenshots of the implementation. The environment currently captures parts of their palette and furnishings, but remains cleaner and smoother than the target.

### Painterly fixer-upper — primary direction

The four-room composition guided the warm palette, vintage fixtures, distinct room identities and readable repair problems. It is the main reference for the desired painterly rendering.

![[painterly-fixer-upper.png]]

### Fixer-upper exploration — condition and history

This exploration informed the age and sense of accumulated repairs: leaks, damaged plaster, worn finishes and mold. Its heavy surface wear is a reference for the apartment's condition, not a literal instruction to make every surface look thickly painted.

![[fixer-upper-exploration.png]]

## Pipeline

Concepts and source models live under `Art Source/`; environment models are built in Blender and imported into Unreal. See the repository README for the rebuild workflow.

Related: [[Audio Direction]] · [[AI Usage Log]]
