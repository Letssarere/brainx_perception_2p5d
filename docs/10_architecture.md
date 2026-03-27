# 아키텍처

## 고정 파이프라인
`depth -> frontend reject/filter -> 2.5D evidence grid -> slot query -> tri-state FSM -> /pickup_2p5d/slot_states`

현재 점유 판단은 depth 중심 경로로 고정한다.
색상 입력은 calibration과 향후 확장용 보조 입력이다.

## 기준 좌표계
- 기준 좌표계는 고정된 `table_frame`이다.
- online plane fitting은 사용하지 않는다.
- YAML로 pickup rectangle을 정의하고, 이를 `12 x 2 = 24` 슬롯 prism으로 분할한다.
- slot id는 image-space 기준 column-major ordering을 따른다.
  - 좌상단 `0`
  - 좌하단 `1`
  - 우상단 `22`
  - 우하단 `23`
- 기본 slot prism 높이 범위는 `z in [0.015, 0.25] m`다.

## 백엔드
- 백엔드는 `table_frame` 기준 `2.5D evidence grid`다.
- 각 cell은 시간 누적 evidence를 유지한다.
  - `height_residual`
  - `valid_count`
  - `occupied_score`
  - `variance`
- 이 grid가 이 트랙의 authoritative geometry/evidence representation이다.

## 슬롯 판정 계층
- slot query는 grid cell을 슬롯 단위로 집계해 evidence metric을 만든다.
  - `occupied_support_ratio`
  - `max_height_m`
  - `visibility_ratio`
- tri-state FSM이 최종 상태를 결정한다.
- `UNKNOWN`은 관측 불충분 상태이며, `FREE`의 약한 형태가 아니다.

## 하드 제약
- backend를 `nvblox`나 다른 표현으로 교체하지 않는다.
- 하드웨어별 topic 이름, TF 차이, camera pose 차이는 `bringup`에서만 처리한다.
- core 패키지 안에 RealSense wrapper 전용 처리나 device-specific logic를 넣지 않는다.
