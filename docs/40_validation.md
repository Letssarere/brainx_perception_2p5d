# 검증 기준

## 검증 순서
1. interface / contract 확인
2. unit test
3. synthetic live 검증
4. replay equivalence 검증
5. Jetson live integration 검증
6. floor-dev 실제 장면 검증
7. 실제 pickup-zone 검증

## Interface / Unit 검증
필수 커버리지:
- package split 유지
- topic / message 이름 일치
- slot geometry 생성
- column-major slot ordering
- FSM transition
- 기본 grid update behavior

## Synthetic / Replay 검증
acceptance:
- pipeline이 synthetic / replay 모두에서 뜬다
- `/pickup_2p5d/grid`, `/pickup_2p5d/slot_evidence`, `/pickup_2p5d/slot_states`가 발행된다
- static scenario에서 live synthetic과 replay가 같은 stable pattern을 만든다
- headless semantic check가 유지된다
  - `empty_table` -> all `FREE`
  - `occupied_static` -> target slots only
  - `low_visibility` -> target slots `UNKNOWN`
  - `insert_remove` -> `FREE -> OCCUPIED -> FREE`

## Jetson Live Integration 검증
acceptance:
- RealSense topic이 generic input topic으로 remap된다
- `map_node`와 `slots_node`는 core 수정 없이 실행된다
- `/pickup_2p5d/slot_states`가 실제 장면에서 발행된다
- camera TF tree와 `camera_frame` 설정이 연결된다

## Floor-dev 검증
목적:
- 실제 pickup-zone 이전에 taped rectangle을 `table_frame` 대용으로 써서 pose / geometry / threshold를 검증한다

튜닝 순서:
1. `camera_x`
2. `camera_y`
3. `camera_z`
4. `camera_roll`
5. `camera_pitch`
6. `camera_yaw`
7. `geometry.origin_x`
8. `geometry.origin_y`
9. `geometry.width`
10. `geometry.depth`
11. 필요 시 perception threshold
12. 마지막에 FSM visibility / dwell

acceptance:
- empty floor에서 `24`개 슬롯이 모두 `FREE`
- single object에서 의도한 슬롯 영역만 `OCCUPIED`
- deliberate occlusion에서 target slot이 `UNKNOWN`
- raw camera topic + `/tf_static`로 녹화한 bag가 live stable pattern을 재현

## Real Bag 캡처
```bash
ros2 bag record \
  /camera/depth/image_rect_raw \
  /camera/depth/camera_info \
  /camera/color/image_raw \
  /camera/color/camera_info \
  /tf_static
```

## Real Bag Replay
```bash
ros2 launch brainx_perception_2p5d_bringup table_2p5d_replay.launch.py \
  bag_path:=/path/to/bag \
  depth_topic:=/camera/depth/image_rect_raw \
  camera_info_topic:=/camera/depth/camera_info \
  color_topic:=/camera/color/image_raw \
  color_camera_info_topic:=/camera/color/camera_info \
  replay_tf_static:=true \
  publish_table_tf:=false
```

`publish_table_tf:=false`로 두어 bag 안의 static TF만 사용하게 한다.
