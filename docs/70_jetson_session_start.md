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
1. Connect RealSense depth and camera info to:
   - `/pickup_2p5d/input/depth`
   - `/pickup_2p5d/input/camera_info`
2. Provide correct `table_frame` TF.
3. Replace synthetic assumptions with real table and pickup rectangle measurements.
4. Capture real bags for:
   - empty table
   - occupied slots
   - insert/remove
   - glare / low-visibility
5. Tune bringup/config values only as needed.
6. Validate that ambiguous observations become `UNKNOWN`, not false `FREE`.

Do not do on Jetson:
- change the message contracts
- redesign the backend away from `2.5D evidence grid`
- introduce online plane fitting
- move hardware-specific logic into core packages

## First Jetson Tasks
1. Inspect current camera and TF sources.
2. Create or adapt a Jetson launch/remap path that feeds the core topics.
3. Confirm a real depth frame reaches `/pickup_2p5d/input/depth`.
4. Confirm `map_node` and `slots_node` run unchanged.
5. Verify `/pickup_2p5d/slot_states` publishes in the real setup.
6. Only then start threshold and performance tuning.

## First Success Criteria
- one Jetson launch starts the pipeline end to end
- a real empty table does not produce false `OCCUPIED`
- low-confidence real scenes produce `UNKNOWN` instead of false `FREE`
- at least one real recorded bag can be replayed for later Mac-side regression checks

## Suggested New-Session Prompt
Use this in the new Jetson session:

```text
Read AGENTS.md, docs/70_jetson_session_start.md, docs/40_jetson_handoff.md, and docs/10_interfaces.md first.
Then inspect the current bringup and implement the smallest Jetson integration path that feeds RealSense depth and camera_info into /pickup_2p5d/input/depth and /pickup_2p5d/input/camera_info without changing the core package architecture.
After that, verify the pipeline publishes /pickup_2p5d/slot_states on Jetson and identify the next real-scene tuning tasks.
```
