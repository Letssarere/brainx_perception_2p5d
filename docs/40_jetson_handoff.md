# Jetson Handoff

## Purpose
Jetson work starts only after the Mac-side core path is stable.

## What Moves to Jetson
- RealSense input source
- actual `table_frame` and pickup rectangle measurements
- device-specific launch and remaps
- performance tuning
- real-scene validation

## Jetson Integration Policy
- `realsense-ros` is launched separately on Jetson.
- This repo should add its own Jetson bringup launch to consume the RealSense topics:
  - `table_2p5d_jetson.launch.py`
- The connection from RealSense topics into:
  - `/pickup_2p5d/input/depth`
  - `/pickup_2p5d/input/camera_info`
  - `/pickup_2p5d/input/color`
  - `/pickup_2p5d/input/color_camera_info`
  should be done with ROS 2 `launch` remappings inside this repo.
- Do not add a relay or republish node just to rename topics.
- Keep RealSense-specific handling in the Jetson bringup layer, not in the core packages.
- The default Jetson mapping is:
  - `/camera/depth/image_rect_raw`
  - `/camera/depth/camera_info`
  - `/camera/color/image_raw`
  - `/camera/color/camera_info`
  - `camera_frame:=camera_link`
  - `camera_roll:=3.141592653589793`
  - `camera_pitch:=0.0`
  - `camera_yaw:=0.0`
  and should be overridden at launch if the active RealSense graph uses aligned-depth or a different
  root frame, or if the camera pose is oblique and needs explicit orientation.

## Jetson Tasks
1. Connect RealSense wrapper topics to:
   - `/pickup_2p5d/input/depth`
   - `/pickup_2p5d/input/camera_info`
   - `/pickup_2p5d/input/color`
   - `/pickup_2p5d/input/color_camera_info`
   - by using `table_2p5d_jetson.launch.py` in this repo to remap the RealSense topics
2. Load actual geometry YAML values.
3. Verify TF and camera orientation.
4. Run empty-table, insert, remove, and glare scenarios.
5. Measure:
   - latency
   - jitter
   - false positives
   - false negatives
6. Adjust thresholds and bringup config only as needed.

## Jetson-specific Rule
Jetson should not be the place where major architecture or message changes are introduced.
Jetson work is integration and tuning work.
