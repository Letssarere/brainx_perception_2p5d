# Architecture

## Goal
Detect 24 pickup-slot occupancy states robustly using a `table-centric 2.5D` backend.

Final output is always:
- `FREE`
- `OCCUPIED`
- `UNKNOWN`

## Fixed Pipeline
`depth -> frontend reject/filter -> 2.5D evidence grid -> slot query -> tri-state FSM -> /pickup_2p5d/slot_states`

## Coordinate System
- Use a fixed `table_frame`.
- Do not use online plane fitting.
- Load a pickup rectangle from YAML.
- Split the rectangle into `12 x 2 = 24` slot prisms.
- Slot IDs are row-major:
  - front row `0..11`
  - back row `12..23`
- Slot prism height range:
  - `z in [0.015, 0.25] m`

## Backend
The backend is a `2.5D evidence grid` defined in `table_frame`.

Each cell maintains time-accumulated evidence such as:
- `height_residual`
- `valid_count`
- `occupied_score`
- `variance`

The grid is the authoritative geometry/evidence representation for this track.

## Slot Decision Layer
Slot query aggregates grid cells per slot and produces evidence metrics such as:
- `occupied_support_ratio`
- `max_height_m`
- `visibility_ratio`

These are passed into a tri-state FSM which owns the final slot state.

## Package Responsibilities
- `brainx_perception_2p5d_msgs`
  - message contracts
- `brainx_perception_2p5d_map`
  - depth filter
  - 2.5D grid generation
- `brainx_perception_2p5d_slots`
  - slot layout
  - slot query
  - FSM
- `brainx_perception_2p5d_bringup`
  - launch
  - config
  - RViz
  - remaps for Mac and Jetson
