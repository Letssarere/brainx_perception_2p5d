# Floor Dev Profile

## Purpose
Use a taped rectangle on the floor as a temporary `table_frame` so the live RealSense path can be tuned
before moving to the actual pickup-zone table.

## Entry Point
- launch: `table_2p5d_floor_dev.launch.py`
- config: `brainx_perception_2p5d_bringup/config/table_2p5d_floor_dev.yaml`

Default topics:
- `/camera/depth/image_rect_raw`
- `/camera/depth/camera_info`
- `/camera/color/image_raw`
- `/camera/color/camera_info`

Default TF args:
- `camera_frame:=camera_link`
- `camera_x:=0.6`
- `camera_y:=0.2`
- `camera_z:=1.1`
- `camera_roll:=3.141592653589793`
- `camera_pitch:=0.0`
- `camera_yaw:=0.0`

## Physical Setup
1. Tape a temporary rectangle on the floor.
2. Start with the repo default rectangle size:
   - width `1.2 m`
   - depth `0.4 m`
3. If possible, add light internal marks for the `12 x 2` slot boundaries so RViz output is easier to judge.
4. Keep the camera on the same oblique view used for development.

## Tuning Order
1. Launch RViz and align the pose first:
   - `camera_x`
   - `camera_y`
   - `camera_z`
   - `camera_roll`
   - `camera_pitch`
   - `camera_yaw`
2. Only after marker alignment, tune rectangle geometry:
   - `geometry.origin_x`
   - `geometry.origin_y`
   - `geometry.width`
   - `geometry.depth`
3. Tune perception thresholds only after pose and rectangle alignment:
   - `perception.min_depth_m`
   - `perception.max_depth_m`
   - `perception.occupied_height_threshold_m`
   - `perception.occupied_score_threshold`
4. Tune FSM visibility and dwell thresholds last.

## Validation Sequence
1. Empty floor:
   - all `24` slots should converge to `FREE`
   - any persistent `OCCUPIED` means pose or geometry is still wrong, or thresholds are too aggressive
2. Single object:
   - place one box in a known slot region
   - only the intended slot area should become `OCCUPIED`
3. Occlusion:
   - partially block the camera view over a target slot
   - the target should become `UNKNOWN`, not false `FREE`

## Replay Capture
Record the raw camera topics plus `/tf_static`:

```bash
ros2 bag record \
  /camera/depth/image_rect_raw \
  /camera/depth/camera_info \
  /camera/color/image_raw \
  /camera/color/camera_info \
  /tf_static
```

Replay with:

```bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_replay.launch.py \
  bag_path:=/path/to/bag \
  depth_topic:=/camera/depth/image_rect_raw \
  camera_info_topic:=/camera/depth/camera_info \
  color_topic:=/camera/color/image_raw \
  color_camera_info_topic:=/camera/color/camera_info \
  replay_tf_static:=true \
  publish_table_tf:=false
```

Disable `publish_table_tf` during replay so the bagged `table_frame -> camera_frame` transform is the
only source of that static TF.
