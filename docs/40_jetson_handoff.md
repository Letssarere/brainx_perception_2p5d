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
- This repo should add its own Jetson bringup launch to consume the RealSense topics.
- The connection from RealSense topics into:
  - `/pickup_2p5d/input/depth`
  - `/pickup_2p5d/input/camera_info`
  should be done with ROS 2 `launch` remappings inside this repo.
- Do not add a relay or republish node just to rename topics.
- Keep RealSense-specific handling in the Jetson bringup layer, not in the core packages.

## Jetson Tasks
1. Connect RealSense wrapper topics to:
   - `/pickup_2p5d/input/depth`
   - `/pickup_2p5d/input/camera_info`
   - by adding a Jetson-side launch in this repo that remaps the RealSense topics
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
