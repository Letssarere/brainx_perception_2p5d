# 현재 개발 상태

## 마지막 업데이트
- date: `2026-03-27`

## 최신 기준선
- branch: `main`
- commit: `cb5876a`
- tag: `v0.1.0-floor-dev`

## 현재 단계
- core 구조와 synthetic / replay 경로는 안정화되어 있다.
- live RealSense 입력을 받는 Jetson / floor-dev 경로도 구현되어 있다.
- 현재 active work는 `floor-dev` 장면에서 pose / geometry / threshold를 맞추고 real bag를 확보하는 것이다.

## 지금 동작하는 것
- `brainx_perception_2p5d_map`, `brainx_perception_2p5d_slots`, `brainx_perception_2p5d_bringup` build / test가 Ubuntu Humble 기준으로 통과한다.
- `table_2p5d_synthetic.launch.py`와 `table_2p5d_replay.launch.py`가 같은 core pipeline을 사용한다.
- synthetic semantic check는 현재 기대 상태를 만족한다.
  - `empty_table` -> all `FREE`
  - `occupied_static` -> target slots only
  - `low_visibility` -> target slots `UNKNOWN`
  - `insert_remove` -> `FREE -> OCCUPIED -> FREE`
- `table_2p5d_jetson.launch.py`가 raw RealSense 기본 topic을 generic input으로 연결한다.
- `table_2p5d_floor_dev.launch.py`와 `table_2p5d_floor_dev.yaml`이 taped rectangle 기반 실환경 튜닝 entrypoint로 준비되어 있다.
- real raw topic + `/tf_static`를 bag로 녹화하고 `table_2p5d_replay.launch.py`로 재생하는 경로가 동작한다.

## 아직 닫히지 않은 것
- floor-dev 장면에서 `empty floor -> 24 FREE`를 아직 맞추지 못했다.
- floor-dev 장면에서 `single object -> target slot only OCCUPIED`를 아직 검증하지 못했다.
- floor-dev 장면에서 `occlusion -> UNKNOWN`를 아직 검증하지 못했다.
- 실제 pickup-zone 테이블 기준 geometry와 threshold는 아직 고정되지 않았다.

## 현재 리스크 / 메모
- 현재 개발용 live 카메라는 실제 pickup-zone 카메라가 아니라 바닥을 비스듬히 보는 개발용 카메라다.
- live / replay 경로는 동작하지만, pose / geometry가 아직 맞지 않아 real floor-dev 장면에서는 slot pattern이 전부 `UNKNOWN`으로 수렴할 수 있다.
- real scene에서 reflective surface나 low visibility가 심하면 baseline-map 확장이 필요할 가능성은 남아 있다.

## 다음 작업 우선순위
1. `table_2p5d_floor_dev.launch.py`로 RViz를 띄워 `camera_x/y/z/roll/pitch/yaw`를 먼저 맞춘다.
2. `geometry.origin_x/origin_y/width/depth`를 맞춰 empty floor에서 `24 FREE`를 만든다.
3. single object와 deliberate occlusion을 검증하고 필요 시 threshold를 미세 조정한다.
4. `empty / one_object / occlusion` real bag를 저장하고 replay equivalence를 확인한다.
5. floor-dev에서 검증된 값을 실제 pickup-zone 측정치로 옮길 준비를 한다.

## 마지막 검증 명령
Ubuntu / Jetson workspace root 기준:

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

live floor-dev 확인:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_floor_dev.launch.py \
  headless:=true
```

real bag replay 확인:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_replay.launch.py \
  bag_path:=/path/to/bag \
  depth_topic:=/camera/depth/image_rect_raw \
  camera_info_topic:=/camera/depth/camera_info \
  color_topic:=/camera/color/image_raw \
  color_camera_info_topic:=/camera/color/camera_info \
  replay_tf_static:=true \
  publish_table_tf:=false
```

## 다음 세션 재개 체크리스트
1. `README.md`와 이 문서를 먼저 읽는다.
2. 현재 RealSense topic 이름과 `camera_frame`이 여전히 기본값과 맞는지 확인한다.
3. `table_2p5d_floor_dev.launch.py`를 띄우고 RViz에서 marker alignment부터 시작한다.
4. pose를 먼저 맞추고, 그 다음 geometry, 마지막에 threshold를 조정한다.
5. 검증 결과가 바뀌면 이 문서와 필요한 canonical 문서를 같은 세션에 갱신한다.
