# 🤖 TurtleBot3 자율주행 실행 가이드(Nav2, waypoint)

## 개요

Windows PC에서 코드를 수정 및 업로드하고, Ubuntu PC에서 빌드 후 TurtleBot3를 자율주행시키는 전체 과정입니다.
자율주행에 앞서 SLAM으로 지도를 먼저 생성해야 합니다.

---

## Part 1 — SLAM: 지도 생성

### 1단계 — 로봇과 카토그래퍼 실행

> 주의: 모든 터미널에 `ROS_DOMAIN_ID=27` 설정이 필수입니다.

**터미널 1 — 로봇 본체 (SSH 접속)**

```
ssh 내가 정한 이름@192.168.0.222
export ROS_DOMAIN_ID=27
ros2 launch turtlebot3_bringup robot.launch.py
```

터미널 2 — 카토그래퍼 실행 (PC)

```
export ROS_DOMAIN_ID=27
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=false
```

### 2단계 — 키보드로 직접 지도 그리기

터미널 3 — 키보드 조종 (PC)

```
export ROS_DOMAIN_ID=27
export TURTLEBOT3_MODEL=waffle_pi
ros2 run turtlebot3_teleop teleop_keyboard
```

> **조작 팁:** 경기장을 주행할 때 벽면이 LiDAR 스캔 데이터(빨간 점들)로 빈틈없이 채워지도록 천천히 이동하세요.
> 특히 가운데 얇은 칸막이 구간은 속도를 낮춰야 지도가 깨지지 않습니다.

### 3단계 — 지도 저장

RViz에서 지도가 하얗게 완성된 것을 확인한 뒤, 터미널을 끄기 전에 새 터미널에서 저장합니다.

터미널 4 — 맵 저장 (PC)

```bash
cd ~/my_ws/src/my_bot/map
ros2 run nav2_map_server map_saver_cli -f my_map
```

저장 완료 시 `my_map.pgm`과 `my_map.yaml` 두 파일이 생성됩니다.

---



## Part 2 — 자율주행 실행

---

## 1단계 — Windows PC: 코드 수정 및 GitHub 업로드


VS Code에서 `tb3_localization.launch.py`와 `setup.py`를 수정한 뒤 GitHub에 push합니다.

```
# 수정한 파일 스테이징
git add .

# 커밋
git commit -m "Final: Add navigation and map path to setup.py"

# GitHub 업로드
git push origin main
```

---

## 2단계 — Ubuntu PC: 코드 수신 및 빌드

로봇과 연결된 Ubuntu PC 터미널을 열고 최신 코드를 받아 빌드합니다.

```
# 패키지 폴더로 이동 후 최신 코드 pull
cd ~/my_ws/src/my_bot
git pull origin main

# 워크스페이스 루트로 이동 후 빌드
cd ~/my_ws
colcon build --packages-select my_bot

# 빌드 결과 현재 터미널에 반영
source install/setup.bash
```

---

## 3단계 — 실전 주행: 터미널 3개 순서대로 실행

> 주의: 모든 터미널에 `ROS_DOMAIN_ID=27` 설정이 필수

### 터미널 1 — 로봇 본체 (SSH 접속)

```
ssh 내가 정한 이름@192.168.0.222
export ROS_DOMAIN_ID=27
ros2 launch turtlebot3_bringup robot.launch.py
```

### 터미널 2 — 자율주행 실행 (Ubuntu PC)

```
export ROS_DOMAIN_ID=27
export TURTLEBOT3_MODEL=waffle_pi
source ~/my_ws/install/setup.bash

# 통합 런치 실행 (위치 추정 + 내비게이션 + RViz)
ros2 launch my_bot tb3_localization.launch.py
```

---

## 4단계 — RViz 조작

런치 파일 실행 후 RViz 창이 뜨면 아래 순서로 조작합니다.

### 위치 초기화 (2D Pose Estimate)

1. 상단 메뉴의 2D Pose Estimate 아이콘 클릭
2. 지도 위 로봇의 실제 위치를 클릭한 채로, 로봇이 바라보는 방향으로 드래그
3. 확인: 초록색 화살표(파티클)들이 로봇 주변으로 모이면 성공

### 목적지 설정 (Nav2 Goal)

1. 2D Pose 설정 후 5~10초 대기 (서버 활성화 시간)
2. 상단 메뉴의 Nav2 Goal 아이콘 클릭
3. 지도에서 목적지를 클릭한 채로 방향 드래그
4. 확인: 지도에 경로가 그려지고 로봇이 출발하면 성공
