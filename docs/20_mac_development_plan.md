# Mac Development Plan

## Purpose
Use macOS to complete the core implementation without hardware dependency.

## Ordered Steps
1. Finalize docs and message contracts.
2. Implement slot geometry library.
3. Implement tri-state FSM as an isolated unit.
4. Implement the minimum depth filter skeleton.
5. Implement the minimum 2.5D evidence grid skeleton.
6. Implement slot query over the 2.5D grid.
7. Connect slot query to the FSM via evidence messages.
8. Create replay or synthetic launch files.
   - `table_2p5d_synthetic.launch.py`
   - `table_2p5d_replay.launch.py`
9. Add RViz markers for:
   - slot prisms
   - slot states
   - 2.5D grid debug view
10. Add unit tests and a deterministic replay validation path.

## Mac-first Constraints
- Do not assume RealSense wrapper availability.
- Do not depend on Jetson-only packages in core packages.
- Use synthetic or replayed inputs for demo readiness.
- Use the Miniconda `ros_env` environment for ROS 2 build, launch, and test commands on macOS.

## Mac Demo Definition
The Mac demo is complete when:
- both `table_2p5d_synthetic.launch.py` and `table_2p5d_replay.launch.py` start the same pipeline
- a synthetic bag can be generated on demand with `generate_synthetic_bag.py`
- slot states are published
- RViz shows slot and grid debug markers
- unit tests for geometry and FSM pass
- the headless smoke path can validate:
  - `empty_table` -> all `FREE`
  - `occupied_static` -> only designated occupied slots
  - `low_visibility` -> designated slots remain `UNKNOWN`
  - `insert_remove` -> `FREE -> OCCUPIED -> FREE`
- replay and live synthetic produce the same stable `SlotStateArray` for static scenarios
