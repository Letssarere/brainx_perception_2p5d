# brainx_perception_2p5d

`brainx_perception_2p5d`는 픽업 슬롯 24칸의 점유 상태를 `table-centric 2.5D` 방식으로 판단하는 기능 저장소다.

## 현재 단계
- synthetic / replay / Jetson / floor-dev 진입 경로는 구현되어 있다.
- 현재 우선순위는 `floor-dev` 장면에서 pose와 geometry를 맞추고, real bag를 확보하는 것이다.
- 최신 기준선은 `v0.1.0-floor-dev` 태그다.

## 패키지 구성
- `brainx_perception_2p5d_msgs`
  - public/internal 메시지 계약
- `brainx_perception_2p5d_map`
  - depth filter와 2.5D evidence grid 생성
- `brainx_perception_2p5d_slots`
  - slot layout, slot query, tri-state FSM
- `brainx_perception_2p5d_bringup`
  - launch, YAML, RViz, synthetic/replay/live integration

## 핵심 파이프라인
`depth -> frontend reject/filter -> 2.5D evidence grid -> slot query -> tri-state FSM -> /pickup_2p5d/slot_states`

## 빠른 시작
Ubuntu / Jetson 기준:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select \
  brainx_perception_2p5d_map \
  brainx_perception_2p5d_slots \
  brainx_perception_2p5d_bringup

source install/setup.bash
colcon test --packages-select \
  brainx_perception_2p5d_map \
  brainx_perception_2p5d_slots \
  brainx_perception_2p5d_bringup \
  --event-handlers console_direct+
```

주요 entrypoint:

```bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_synthetic.launch.py
ros2 launch brainx_perception_2p5d_bringup table_2p5d_replay.launch.py bag_path:=/path/to/bag
ros2 launch brainx_perception_2p5d_bringup table_2p5d_jetson.launch.py headless:=true
ros2 launch brainx_perception_2p5d_bringup table_2p5d_floor_dev.launch.py
```

현재 live 입력 기본값:
- `/camera/depth/image_rect_raw`
- `/camera/depth/camera_info`
- `/camera/color/image_raw`
- `/camera/color/camera_info`
- `camera_frame:=camera_link`

## 새 세션 시작 순서
1. `README.md`
2. [현재 개발 상태](docs/90_current_status.md)
3. 필요 시 [프로젝트 개요](docs/00_project_overview.md)
4. 필요 시 [아키텍처](docs/10_architecture.md)
5. 필요 시 [인터페이스](docs/20_interfaces.md)
6. 필요 시 [개발 워크플로](docs/30_workflow.md)
7. 필요 시 [검증 기준](docs/40_validation.md)

## 문서
- [프로젝트 개요](docs/00_project_overview.md)
- [아키텍처](docs/10_architecture.md)
- [인터페이스](docs/20_interfaces.md)
- [개발 워크플로](docs/30_workflow.md)
- [검증 기준](docs/40_validation.md)
- [현재 개발 상태](docs/90_current_status.md)
