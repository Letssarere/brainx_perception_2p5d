# Interfaces

## Namespaces
Use `/pickup_2p5d/...` as the default namespace for this repo.

## Input Topics
Core nodes should consume generic input topics:
- `/pickup_2p5d/input/depth`
- `/pickup_2p5d/input/camera_info`
- `/pickup_2p5d/input/color`
- `/pickup_2p5d/input/color_camera_info`

TF is also required and must include `table_frame`.

On Jetson, hardware-specific topic names should be adapted to these generic inputs in the bringup layer with ROS 2 launch remappings.
Do not introduce a relay node only to rename RealSense topics.
The Jetson bringup entrypoint is `table_2p5d_jetson.launch.py`, which defaults to:
- `/camera/depth/image_rect_raw`
- `/camera/depth/camera_info`
- `/camera/color/image_raw`
- `/camera/color/camera_info`
and allows launch-arg overrides for aligned-depth or other camera namespaces. When the camera already
publishes a TF tree, use the root frame such as `camera_link` for `camera_frame`, not the optical frame.
Oblique real-scene setups should also override `camera_roll`, `camera_pitch`, and `camera_yaw` instead
of assuming the baked-in top-down transform.

The current occupancy pipeline remains depth-driven. The color stream is an auxiliary input reserved for calibration and future tasks.

## Internal and Public Topics
- `/pickup_2p5d/depth_validated`
- `/pickup_2p5d/visibility_mask`
- `/pickup_2p5d/grid`
- `/pickup_2p5d/slot_evidence`
- `/pickup_2p5d/slot_states`
- `/pickup_2p5d/slot_markers`

## Message Contracts
### Public State Messages
- `SlotState.msg`
- `SlotStateArray.msg`

These are the externally meaningful outputs and should remain stable.

### Internal Evidence Messages
- `SlotEvidence.msg`
- `SlotEvidenceArray.msg`

These decouple slot query from the FSM.

Recommended evidence content:
- slot id
- evidence category
- occupied support ratio
- max height
- visibility ratio
- optional confidence

## Config Groups
Configuration should be split into:
- `geometry`
  - `table_frame`
  - pickup rectangle
  - slot layout
- `perception`
  - depth filter thresholds
  - visibility rules
  - grid parameters
- `fsm`
  - dwell/hysteresis settings
  - evidence thresholds

## Launch Entry Points
- `table_2p5d_synthetic.launch.py`
- `table_2p5d_replay.launch.py`
- `table_2p5d_jetson.launch.py`
- `table_2p5d_floor_dev.launch.py`
- `generate_synthetic_bag.py`

The synthetic launch is the primary live Mac entrypoint.
The replay launch reuses the same pipeline and accepts `bag_path`.
The Jetson launch reuses the same pipeline and remaps external camera topics into the core input topics.
The floor-dev launch reuses the same pipeline with a dedicated config for a taped floor rectangle and
explicit camera pose tuning.
`generate_synthetic_bag.py` creates deterministic replay fixtures on demand.
