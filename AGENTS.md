# brainx_perception_2p5d Agent Guide

## Fixed Principles
- This repository is the dedicated `table-centric 2.5D occupancy` track.
- Keep the backend fixed to `2.5D evidence grid`; do not redesign it into `nvblox` or another mapping backend.
- Final output is always 24 slot states with tri-state semantics:
  - `FREE`
  - `OCCUPIED`
  - `UNKNOWN`
- `UNKNOWN` must never be treated as `FREE`.
- Use a fixed `table_frame`; do not introduce online plane fitting.
- Keep the package split fixed:
  - `brainx_perception_2p5d_msgs`
  - `brainx_perception_2p5d_map`
  - `brainx_perception_2p5d_slots`
  - `brainx_perception_2p5d_bringup`

## Development Strategy
- Development is Mac-first and Jetson-second.
- On macOS, finish:
  - docs
  - core logic
  - unit tests
  - replay or synthetic input path
  - RViz-level demo
- On Jetson, finish:
  - RealSense integration
  - performance tuning
  - environment calibration
  - final demo polish

## Implementation Rules
- Core packages must build without Jetson-only or RealSense-wrapper-only dependencies.
- Hardware-specific integration belongs in bringup, remaps, and configuration layers.
- Use generic input topics for the core pipeline:
  - `/pickup_2p5d/input/depth`
  - `/pickup_2p5d/input/camera_info`
- Keep final namespace under `/pickup_2p5d/...`.
- Prefer docs-first changes: update docs before or together with code when behavior changes.

## Architecture Contract
- Pipeline:
  - `depth -> frontend reject/filter -> 2.5D evidence grid -> slot query -> tri-state FSM -> /pickup_2p5d/slot_states`
- Package responsibilities:
  - `msgs`: public and internal message contracts
  - `map`: depth filter and 2.5D grid generation
  - `slots`: slot layout, slot query, FSM
  - `bringup`: launch, YAML, RViz, remaps

## Testing Expectations
- Unit tests must cover:
  - slot geometry generation
  - FSM transitions
  - basic grid update behavior
- Replay or synthetic demo must work on macOS before Jetson integration starts.
- Jetson validation must focus on integration and performance, not major logic redesign.
