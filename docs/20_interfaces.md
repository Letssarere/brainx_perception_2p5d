# 인터페이스

## 네임스페이스
- 기본 네임스페이스는 `/pickup_2p5d/...`를 사용한다.

## Core 입력 토픽
core node는 아래 generic 입력을 소비한다.
- `/pickup_2p5d/input/depth`
- `/pickup_2p5d/input/camera_info`
- `/pickup_2p5d/input/color`
- `/pickup_2p5d/input/color_camera_info`

필수 TF:
- `table_frame`

live camera의 실제 topic 이름은 bringup launch에서 이 generic 입력으로 remap한다.

## 현재 public / internal 토픽
- `/pickup_2p5d/depth_validated`
- `/pickup_2p5d/visibility_mask`
- `/pickup_2p5d/grid`
- `/pickup_2p5d/slot_evidence`
- `/pickup_2p5d/slot_states`
- `/pickup_2p5d/slot_markers`

## 메시지 계약
외부 의미가 있는 public 메시지:
- `SlotState.msg`
- `SlotStateArray.msg`

내부 decoupling용 evidence 메시지:
- `SlotEvidence.msg`
- `SlotEvidenceArray.msg`

## 설정 그룹
- `geometry`
  - `table_frame`
  - pickup rectangle
  - slot layout
- `perception`
  - depth filter threshold
  - visibility rule
  - grid parameter
- `fsm`
  - dwell / hysteresis
  - state transition threshold

## Launch entrypoint
- `table_2p5d_synthetic.launch.py`
  - synthetic live 입력
- `table_2p5d_replay.launch.py`
  - replay bag 입력
- `table_2p5d_jetson.launch.py`
  - live RealSense 입력
- `table_2p5d_floor_dev.launch.py`
  - taped floor rectangle 입력
- `generate_synthetic_bag.py`
  - deterministic replay fixture 생성

## Live 입력 기본값
`table_2p5d_jetson.launch.py`와 `table_2p5d_floor_dev.launch.py`의 기본 camera 입력은 아래를 사용한다.
- `/camera/depth/image_rect_raw`
- `/camera/depth/camera_info`
- `/camera/color/image_raw`
- `/camera/color/camera_info`

기본 camera frame:
- `camera_frame:=camera_link`

camera가 자체 TF tree를 이미 발행한다면 optical frame이 아니라 tree root frame을 `camera_frame`으로 사용한다.
비스듬한 시점이면 `camera_roll`, `camera_pitch`, `camera_yaw`를 launch argument로 명시한다.
