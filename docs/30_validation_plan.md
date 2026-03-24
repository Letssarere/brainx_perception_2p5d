# Validation Plan

## Validation Order
1. Interface validation
2. Unit validation
3. Replay or synthetic end-to-end validation
4. Jetson hardware integration validation

## Interface Validation
- package names match the intended `brainx_perception_2p5d_*` split
- topics follow `/pickup_2p5d/...`
- docs and code use the same message names

## Unit Validation
Must cover:
- slot geometry generation from a pickup rectangle
- row-major slot ID ordering
- FSM state transitions
- minimum grid update behavior

## Replay or Synthetic Validation
Mac-side acceptance:
- pipeline starts from replay or synthetic input
- grid is updated
- slot evidence is published
- final slot states are published
- RViz markers are visible and coherent

## Jetson Validation
Acceptance on Jetson:
- RealSense topics remap into generic input topics
- `table_frame` config matches the real setup
- empty table remains stable
- cup insert/remove transitions are sensible
- glare or poor visibility yields `UNKNOWN` rather than false `FREE`

## Success Criteria
- Mac demo works without hardware dependencies
- Jetson integration changes are limited to input/remap/config/performance tuning
