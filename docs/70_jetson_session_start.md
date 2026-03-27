# Jetson Session Start

## Read This First
Open these files in this order:
1. `AGENTS.md`
2. `docs/70_jetson_session_start.md`
3. `docs/40_jetson_handoff.md`
4. `docs/10_interfaces.md`

## Current Repo State
- Mac-first implementation is complete enough to move to Jetson integration.
- The backend is fixed to `2.5D evidence grid`.
- Final output remains `24` slot states with:
  - `FREE`
  - `OCCUPIED`
  - `UNKNOWN`
- `UNKNOWN` must never be treated as `FREE`.

## What Already Works
- live synthetic demo:
  - `table_2p5d_synthetic.launch.py`
- deterministic replay demo:
  - `table_2p5d_replay.launch.py`
  - `generate_synthetic_bag.py`
- stable Mac semantic checks:
  - `empty_table` -> all `FREE`
  - `occupied_static` -> only target slots `OCCUPIED`
  - `low_visibility` -> target slots remain `UNKNOWN`
  - `insert_remove` -> `FREE -> OCCUPIED -> FREE`
- replay and live synthetic produce the same stable `SlotStateArray` for static scenarios

## Last Verified Baseline
- commit: `bd3b3e6`
- macOS validation was run in Miniconda `ros_env`
- verified commands:
```bash
conda run -n ros_env colcon build --symlink-install --packages-select \
  brainx_perception_2p5d_map \
  brainx_perception_2p5d_slots \
  brainx_perception_2p5d_bringup

conda run -n ros_env bash -lc 'source install/setup.bash && \
  colcon test --packages-select \
    brainx_perception_2p5d_slots \
    brainx_perception_2p5d_bringup \
    --event-handlers console_direct+'
```

## Jetson Scope
Jetson work is integration and real-scene tuning, not architecture redesign.

Do on Jetson:
1. Launch `realsense-ros` separately.
2. Add or adapt a Jetson launch in this repo that remaps RealSense topics into:
   - `/pickup_2p5d/input/depth`
   - `/pickup_2p5d/input/camera_info`
   - `/pickup_2p5d/input/color`
   - `/pickup_2p5d/input/color_camera_info`
   - current repo entrypoint: `table_2p5d_jetson.launch.py`
   - current defaults:
     - `/camera/depth/image_rect_raw`
     - `/camera/depth/camera_info`
     - `/camera/color/image_raw`
     - `/camera/color/camera_info`
     - `camera_frame:=camera_link`
     - `camera_roll:=3.141592653589793`
     - `camera_pitch:=0.0`
     - `camera_yaw:=0.0`
3. Provide correct `table_frame` TF.
4. Replace synthetic assumptions with real table and pickup rectangle measurements.
5. Capture real bags for:
   - empty table
   - occupied slots
   - insert/remove
   - glare / low-visibility
6. Tune bringup/config values only as needed.
7. Validate that ambiguous observations become `UNKNOWN`, not false `FREE`.

Do not do on Jetson:
- change the message contracts
- redesign the backend away from `2.5D evidence grid`
- introduce online plane fitting
- move hardware-specific logic into core packages
- add a relay/republish node only to rename RealSense topics

## First Jetson Tasks
1. Inspect the RealSense topic names and camera frame names on Jetson.
2. Create or adapt a Jetson launch in this repo that remaps those topics into the core input topics.
   - use `table_2p5d_jetson.launch.py`
   - override `depth_topic`, `camera_info_topic`, or `camera_frame` if the live graph differs from the defaults
   - when the camera already publishes its own TF tree, point `camera_frame` at the tree root, not the optical frame
   - if the live camera view is oblique, override `camera_roll/pitch/yaw` instead of assuming the default transform
3. Confirm a real depth frame reaches `/pickup_2p5d/input/depth`.
4. Confirm matching camera info reaches `/pickup_2p5d/input/camera_info`.
5. Confirm color image and color camera info reach the generic input topics.
6. Confirm `map_node` and `slots_node` run unchanged.
7. Verify `/pickup_2p5d/slot_states` publishes in the real setup.
8. Only then start threshold and performance tuning.

## First Success Criteria
- one Jetson launch starts the pipeline end to end
- default Jetson launch works with raw RealSense depth:
  - `/camera/depth/image_rect_raw`
  - `/camera/depth/camera_info`
- default Jetson launch also remaps raw RealSense color:
  - `/camera/color/image_raw`
  - `/camera/color/camera_info`
- a real empty table does not produce false `OCCUPIED`
- low-confidence real scenes produce `UNKNOWN` instead of false `FREE`
- at least one real recorded bag can be replayed for later Mac-side regression checks

## Suggested New-Session Prompt
Use this in the new Jetson session:

```text
Read AGENTS.md, docs/70_jetson_session_start.md, docs/40_jetson_handoff.md, and docs/10_interfaces.md first.
Then inspect the current bringup and implement the smallest Jetson integration path that feeds RealSense depth and camera_info into /pickup_2p5d/input/depth and /pickup_2p5d/input/camera_info without changing the core package architecture.
Assume realsense-ros is launched separately, and implement the integration on this repo side with ROS 2 launch remappings rather than a relay node.
After that, verify the pipeline publishes /pickup_2p5d/slot_states on Jetson and identify the next real-scene tuning tasks.
```
