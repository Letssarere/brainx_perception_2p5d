# Replay-Ready Handoff

## Date
- 2026-03-24

## Goal Of This Work Slice
- split the Mac demo into:
  - `table_2p5d_synthetic.launch.py`
  - `table_2p5d_replay.launch.py`
- add a shared synthetic scene renderer
- add deterministic rosbag generation
- add replay/live validation scaffolding
- keep all ROS 2 build/test commands on macOS inside the Miniconda `ros_env`

## What Is Implemented
- `brainx_perception_2p5d_bringup` now has a shared Python package:
  - `brainx_perception_2p5d_bringup/synthetic_scene.py`
  - `brainx_perception_2p5d_bringup/synthetic_depth_publisher.py`
  - `brainx_perception_2p5d_bringup/generate_synthetic_bag.py`
  - `brainx_perception_2p5d_bringup/test_support.py`
- launch split is in place:
  - `brainx_perception_2p5d_bringup/launch/table_2p5d_synthetic.launch.py`
  - `brainx_perception_2p5d_bringup/launch/table_2p5d_replay.launch.py`
  - shared include:
    - `brainx_perception_2p5d_bringup/launch/includes/table_2p5d_pipeline.launch.py`
- wrapper scripts are installed:
  - `brainx_perception_2p5d_bringup/scripts/synthetic_depth_publisher.py`
  - `brainx_perception_2p5d_bringup/scripts/generate_synthetic_bag.py`
- deterministic bag generation works via `rosbag2_py`
- `brainx_perception_2p5d_slots` has an additional unit test:
  - `brainx_perception_2p5d_slots/test/test_slot_query.cpp`

## What Was Verified
- build passed in `ros_env`:
  - `conda run -n ros_env colcon build --symlink-install --packages-select brainx_perception_2p5d_map brainx_perception_2p5d_slots brainx_perception_2p5d_bringup`
- slots unit tests passed in `ros_env`
- bringup package installs and launches
- bag generation works and produces replayable `rosbag2` output
- live synthetic and replay can both publish `/pickup_2p5d/slot_states`

## Current Blockers
- the replay-ready infrastructure is mostly in place, but the synthetic scenario semantics are not tuned enough yet
- the intended scenario acceptance criteria are not satisfied yet:
  - `empty_table` does not reliably converge to all `FREE`
  - `occupied_static` does not reliably isolate only the designated occupied slots
  - `low_visibility` does not reliably keep the designated slots in `UNKNOWN`
  - `insert_remove` currently produces a stable transition, but not the intended `FREE -> OCCUPIED -> FREE` ordering
- because of that, the current end-to-end bringup tests are still written against the intended behavior and are expected to fail until tuning is finished

## Most Important Findings
- the Python binding of `image_geometry` looks like it returns a unit ray, but the installed C++ header documents `projectPixelTo3dRay()` as returning a ray with `z = 1.0`
- because the production code uses the C++ API, tuning must follow the C++ semantics, not the Python binding behavior
- replay/live differences were partly caused by replay bags being too short; the bag generator now repeats scenario frames multiple times to give the FSM time to settle

## Files To Inspect First On Resume
- `brainx_perception_2p5d_bringup/brainx_perception_2p5d_bringup/synthetic_scene.py`
- `brainx_perception_2p5d_bringup/brainx_perception_2p5d_bringup/generate_synthetic_bag.py`
- `brainx_perception_2p5d_bringup/brainx_perception_2p5d_bringup/test_support.py`
- `brainx_perception_2p5d_bringup/test/test_smoke.py`
- `brainx_perception_2p5d_bringup/test/test_replay_equivalence.py`
- `brainx_perception_2p5d_bringup/config/table_2p5d.yaml`

## Recommended Next Steps
1. simplify and retune the synthetic camera/scene geometry until `empty_table` converges to all `FREE`
2. retune the occupied object footprint and height so `occupied_static` marks only the designated slots
3. widen or reshape the synthetic hidden-depth region so `low_visibility` drives the intended slots into `UNKNOWN`
4. once the live synthetic scenarios are stable, update the bringup tests to match the tuned scenario definitions and rerun replay/live equivalence
5. after tests pass, update `README.md`, `docs/10_interfaces.md`, and `docs/20_mac_development_plan.md` to describe the finalized replay-ready flow

## Estimated Remaining Work
- infrastructure completion: done enough to resume immediately
- synthetic scenario tuning plus test stabilization: about 1 focused engineering session, roughly 2 to 4 hours
- documentation cleanup after tests pass: about 30 minutes
