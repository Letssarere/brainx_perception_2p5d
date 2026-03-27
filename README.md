# brainx_perception_2p5d

`brainx_perception_2p5d` is the dedicated `table-centric 2.5D occupancy` track for pickup-slot detection.

The repository is designed for a two-stage workflow:
- macOS first:
  - define interfaces
  - implement core logic
  - validate with unit tests and replay or synthetic inputs
  - produce a minimum debug/demo flow
- Jetson later:
  - connect RealSense inputs
  - tune for performance and stability
  - validate on real pickup-zone conditions

## Packages
- `brainx_perception_2p5d_msgs`
  - message contracts for slot state and slot evidence
- `brainx_perception_2p5d_map`
  - frontend reject/filter and 2.5D evidence grid generation
- `brainx_perception_2p5d_slots`
  - slot layout, slot query, tri-state FSM
- `brainx_perception_2p5d_bringup`
  - launch files, YAML configs, RViz configs, hardware/remap integration

## Core Pipeline
`depth -> frontend reject/filter -> 2.5D evidence grid -> slot query -> tri-state FSM -> /pickup_2p5d/slot_states`

## Development Flow
1. Read `AGENTS.md` and the files under `docs/`.
2. Lock interfaces and architecture in docs before expanding implementation.
3. Finish a Mac-first replay or synthetic demo.
4. Move to Jetson for camera integration, calibration, and performance tuning.

## Mac Build And Test
Use the Miniconda `ros_env` environment for all ROS 2 commands on macOS.

Build:
```bash
conda run -n ros_env colcon build --symlink-install
```

Test:
```bash
conda run -n ros_env colcon test --packages-select \
  brainx_perception_2p5d_slots \
  brainx_perception_2p5d_bringup
```

Run the live synthetic Mac demo:
```bash
conda run -n ros_env bash -lc 'source install/setup.bash && \
  ros2 launch brainx_perception_2p5d_bringup table_2p5d_synthetic.launch.py'
```

Generate a deterministic synthetic bag:
```bash
conda run -n ros_env bash -lc 'source install/setup.bash && \
  ros2 run brainx_perception_2p5d_bringup generate_synthetic_bag.py \
    --scenario occupied_static'
```

Replay a generated bag:
```bash
conda run -n ros_env bash -lc 'source install/setup.bash && \
  ros2 launch brainx_perception_2p5d_bringup table_2p5d_replay.launch.py \
    bag_path:=/tmp/brainx_2p5d_demo/bag'
```

Run the Jetson RealSense integration path:
```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_jetson.launch.py \
  headless:=true
```

Run the floor-dev integration path against a taped floor rectangle:
```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_floor_dev.launch.py \
  headless:=false
```

Defaults:
- `depth_topic:=/camera/depth/image_rect_raw`
- `camera_info_topic:=/camera/depth/camera_info`
- `color_topic:=/camera/color/image_raw`
- `color_camera_info_topic:=/camera/color/camera_info`
- `camera_frame:=camera_link`
- `camera_roll:=3.141592653589793`
- `camera_pitch:=0.0`
- `camera_yaw:=0.0`

Use the root of the active RealSense TF tree for `camera_frame` so the depth image frame can connect
through the existing camera transforms. Override the launch args if the live graph uses aligned-depth,
a different frame name, or an oblique view that needs explicit `camera_roll/pitch/yaw`.

For real-scene replay, record the raw camera topics plus `/tf_static`, then replay with:
```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_replay.launch.py \
  bag_path:=/tmp/brainx_2p5d_floor_dev/bag \
  depth_topic:=/camera/depth/image_rect_raw \
  camera_info_topic:=/camera/depth/camera_info \
  color_topic:=/camera/color/image_raw \
  color_camera_info_topic:=/camera/color/camera_info \
  replay_tf_static:=true \
  publish_table_tf:=false
```

The current occupancy path remains depth-driven. Color topics are plumbed through as auxiliary inputs for calibration and future tasks.

## Docs
- [Architecture](/Users/junho/brainx_perception_2p5d/docs/00_architecture.md)
- [Interfaces](/Users/junho/brainx_perception_2p5d/docs/10_interfaces.md)
- [Mac Development Plan](/Users/junho/brainx_perception_2p5d/docs/20_mac_development_plan.md)
- [Validation Plan](/Users/junho/brainx_perception_2p5d/docs/30_validation_plan.md)
- [Jetson Handoff](/Users/junho/brainx_perception_2p5d/docs/40_jetson_handoff.md)
- [Jetson Session Start](/Users/junho/brainx_perception_2p5d/docs/70_jetson_session_start.md)
- [Floor Dev Profile](/Users/junho/brainx_perception_2p5d/docs/80_floor_dev_profile.md)
- [Open Issues](/Users/junho/brainx_perception_2p5d/docs/50_open_issues.md)
