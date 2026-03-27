# 프로젝트 개요

## 목적
이 저장소의 목적은 픽업 슬롯 `24`칸 각각에 대해 아래 세 가지 상태를 안정적으로 판단하는 것이다.
- `FREE`
- `OCCUPIED`
- `UNKNOWN`

이 저장소는 `2.5D evidence grid` 기반 구현만 담당한다.

## 현재 범위
- synthetic live 입력
- deterministic replay 입력
- Jetson RealSense live 입력
- floor-dev 검증용 taped-rectangle 입력
- slot state 산출과 디버그 marker 발행

## 비범위
- OTA, fleet rollout, 통합 배포 관리
- online plane fitting
- `nvblox` 등 다른 backend로의 전환
- 임시 relay node를 통한 topic rename
- RGB 중심 점유 판단 경로 재설계

## 패키지 책임 요약
- `brainx_perception_2p5d_msgs`
  - slot state / slot evidence 메시지
- `brainx_perception_2p5d_map`
  - depth filtering
  - 2.5D evidence grid
- `brainx_perception_2p5d_slots`
  - slot layout
  - slot query
  - tri-state FSM
- `brainx_perception_2p5d_bringup`
  - launch
  - YAML config
  - RViz
  - synthetic / replay / live integration

## 현재 개발 단계
- core 구조와 synthetic / replay 경로는 이미 구현되어 있다.
- 현재 active phase는 Jetson / floor-dev 실제 장면 튜닝이다.
- 다음 완료 기준은 floor-dev에서 empty / occupied / occlusion 장면을 안정적으로 재현하고, real bag 기반 replay 회귀 입력을 확보하는 것이다.
