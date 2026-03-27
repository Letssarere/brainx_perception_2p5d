# brainx_perception_2p5d Agent Guide

## 저장소 역할
- 이 저장소는 픽업 슬롯 24칸의 점유 상태를 판단하는 `table-centric 2.5D occupancy` 전용 트랙이다.
- 통합 배포나 OTA 정책은 다른 저장소가 담당하고, 이 저장소는 기능 구현과 검증에 집중한다.

## 고정 불변 조건
- 백엔드는 반드시 `2.5D evidence grid`를 유지한다.
- 최종 출력은 항상 `24`개 슬롯의 tri-state다.
  - `FREE`
  - `OCCUPIED`
  - `UNKNOWN`
- `UNKNOWN`은 절대로 `FREE`로 취급하지 않는다.
- 기준 좌표계는 고정된 `table_frame`이다.
- online plane fitting은 도입하지 않는다.
- 패키지 분리는 아래 구성을 유지한다.
  - `brainx_perception_2p5d_msgs`
  - `brainx_perception_2p5d_map`
  - `brainx_perception_2p5d_slots`
  - `brainx_perception_2p5d_bringup`

## 문서 읽기 순서
- 새 세션 시작 시 아래 순서로 읽는다.
  1. `README.md`
  2. `docs/90_current_status.md`
  3. 필요에 따라 `docs/00_project_overview.md`
  4. 필요에 따라 `docs/10_architecture.md`
  5. 필요에 따라 `docs/20_interfaces.md`
  6. 필요에 따라 `docs/30_workflow.md`
  7. 필요에 따라 `docs/40_validation.md`

## 구현 규칙
- core 패키지는 Jetson 전용 패키지나 RealSense wrapper 전용 의존성에 묶이면 안 된다.
- 하드웨어별 topic remap, TF 입력 차이, 현장 설정은 `bringup` 계층에서만 처리한다.
- core 파이프라인 입력은 항상 generic topic을 사용한다.
  - `/pickup_2p5d/input/depth`
  - `/pickup_2p5d/input/camera_info`
  - `/pickup_2p5d/input/color`
  - `/pickup_2p5d/input/color_camera_info`
- 최종 namespace는 `/pickup_2p5d/...` 아래를 유지한다.
- 색상 입력은 현재 보조 입력이다. 현 점유 판단 경로를 RGB 중심으로 재설계하지 않는다.

## 패키지 책임
- `msgs`
  - 외부/내부 메시지 계약
- `map`
  - depth reject/filter
  - `table_frame` 기준 2.5D grid 생성
- `slots`
  - 슬롯 레이아웃
  - 슬롯별 evidence 집계
  - tri-state FSM
- `bringup`
  - launch
  - config
  - RViz
  - synthetic/replay/live input 연결

## 문서 유지 규칙
- 의미 있는 변경이 있으면 같은 작업 세션 안에서 반드시 `docs/90_current_status.md`를 갱신한다.
- 아래 내용이 바뀌면 대응하는 canonical 문서를 같은 변경에 함께 갱신한다.
  - 구조 변경: `docs/10_architecture.md`
  - 인터페이스 변경: `docs/20_interfaces.md`
  - 개발 절차 변경: `docs/30_workflow.md`
  - 검증 기준 변경: `docs/40_validation.md`
- 임시 handoff 문서, session-start 문서, one-off 진행 로그 문서를 새로 만들지 않는다.
- `docs/90_current_status.md`와 실제 repo 상태가 다르면 작업이 끝난 것으로 보지 않는다.

## 검증 기대치
- unit test는 최소 아래를 계속 커버해야 한다.
  - 슬롯 geometry 생성
  - column-major slot ordering
  - FSM transition
  - 기본 grid update behavior
- synthetic/replay 경로는 계속 회귀 검증용으로 유지한다.
- Jetson과 floor-dev 단계는 구조 변경이 아니라 integration과 tuning 단계로 취급한다.
