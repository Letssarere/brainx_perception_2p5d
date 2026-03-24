# Open Issues

## Known Open Questions
- Whether a static plane is sufficient, or a per-cell empty-table baseline map is needed.
- How much reflective or glass-heavy behavior can be handled without an auxiliary rescue branch.
- Whether `visibility_ratio` alone is sufficient for `UNKNOWN` handling in hard scenes.
- Whether a later RGB or stereo rescue branch should be added.

## Mac-side Risks
- Replay or synthetic data may not reproduce all real-world glare cases.
- Marker-based debug views may look correct while real sensor noise still breaks assumptions.

## Jetson-side Risks
- RealSense topic timing and frame naming may require extra bringup remaps.
- Performance may require grid resolution or visualization simplification.
- Actual display surface behavior may motivate a baseline-map extension.

## Comparison Goal
This repo should remain comparable to the `nvblox` track:
- same slot semantics
- same geometry contract
- same tri-state meaning
- different backend only
