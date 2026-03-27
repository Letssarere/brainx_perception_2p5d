# 개발 워크플로

## 기본 원칙
- 이 저장소의 상태 확인은 `docs/90_current_status.md`를 기준으로 한다.
- 세션 시작 시 먼저 현재 상태 문서를 읽고, 거기에 적힌 next task부터 확인한다.
- 작업이 끝나면 검증을 다시 수행하고, 같은 세션에서 문서를 갱신한다.

## 새 세션 재개 절차
1. `README.md`를 읽는다.
2. `docs/90_current_status.md`를 읽는다.
3. 이번 작업에 필요한 canonical 문서만 추가로 읽는다.
4. `docs/90_current_status.md`에 적힌 마지막 검증 명령을 가능한 범위에서 재현한다.
5. 변경 후 다시 검증하고 상태 문서를 갱신한다.

## 지원 환경
- macOS
  - synthetic / replay 중심 개발
  - `Miniconda ros_env` 사용
- Ubuntu / Jetson
  - live RealSense / floor-dev / 실제 장면 검증
  - `/opt/ros/humble` 기준

## 자주 쓰는 명령
macOS 예시:

```bash
conda run -n ros_env colcon build --symlink-install
conda run -n ros_env colcon test --packages-select \
  brainx_perception_2p5d_slots \
  brainx_perception_2p5d_bringup
```

Ubuntu / Jetson 예시:

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

## 작업 루프
1. 현재 상태 확인
2. 관련 구조 / 인터페이스 문서 확인
3. 변경 구현
4. 변경 범위에 맞는 build / test / launch / replay 검증
5. `docs/90_current_status.md` 갱신
6. 구조 / 인터페이스 / 검증 기준이 바뀌었으면 관련 canonical 문서도 함께 갱신

## 현재 단계별 entrypoint 선택
- synthetic behavior 확인:
  - `table_2p5d_synthetic.launch.py`
- replay regression 확인:
  - `table_2p5d_replay.launch.py`
- live RealSense integration 확인:
  - `table_2p5d_jetson.launch.py`
- taped rectangle 기반 현장형 튜닝:
  - `table_2p5d_floor_dev.launch.py`

## 금지 사항
- 새 handoff 문서나 session-start 문서를 임시로 추가하지 않는다.
- 상태 이력을 별도 수기 로그로 관리하지 않는다.
- 현재 상태는 반드시 `docs/90_current_status.md` 한 곳에 모은다.
