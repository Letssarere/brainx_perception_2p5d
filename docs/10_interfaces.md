# Interfaces

## Namespaces
Use `/pickup_2p5d/...` as the default namespace for this repo.

## Input Topics
Core nodes should consume generic input topics:
- `/pickup_2p5d/input/depth`
- `/pickup_2p5d/input/camera_info`

TF is also required and must include `table_frame`.

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
- `generate_synthetic_bag.py`

The synthetic launch is the primary live Mac entrypoint.
The replay launch reuses the same pipeline and accepts `bag_path`.
`generate_synthetic_bag.py` creates deterministic replay fixtures on demand.
