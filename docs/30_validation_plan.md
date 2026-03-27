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
- column-major slot ID ordering in image space
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

## Floor Dev Validation
Acceptance for the temporary floor-dev profile:
- a taped floor rectangle can be aligned with `table_frame` in RViz
- empty floor remains stable `FREE` across all 24 slots
- one object can drive only the intended slot area to `OCCUPIED`
- deliberate occlusion yields `UNKNOWN` instead of false `FREE`
- a recorded bag with generic input topics and `/tf_static` reproduces the live stable pattern

## Success Criteria
- Mac demo works without hardware dependencies
- Jetson integration changes are limited to input/remap/config/performance tuning
