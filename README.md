💻 1단계: 윈도우 PC (코드 수정 및 업로드)
윈도우 VS Code에서 **tb3_localization.launch.py**와 **setup.py**를 최종본으로 수정하고 깃허브에 쏘는 과정입니다.


# 1. 수정한 파일들 스테이징
git add .

# 2. 커밋 남기기
git commit -m "Final: Add navigation and map path to setup.py"

# 3. 깃허브로 업로드 (rebase 없이 안전하게!)
git push origin main


🤖 2단계: 우분투 PC (코드 수신 및 준비)
이제 로봇과 연결된 우분투 PC 터미널을 열고 최신 코드를 받아 빌드합니다.


# 1. 패키지 폴더 이동 및 최신 코드 다운로드
cd ~/my_ws/src/my_bot
git pull origin main

# 2. 워크스페이스 루트로 이동 후 빌드
cd ~/my_ws
colcon build --packages-select my_bot

# 3. 현재 터미널에 빌드 결과 반영
source install/setup.bash


🚀 3단계: 실전 주행 (터미널 순서대로 실행)
터미널을 총 3개 띄워서 순서대로 입력하세요. 모든 터미널에 도메인 27 설정은 필수입니다!

터미널 1: 로봇 본체 (SSH 접속)

ssh burger@192.168.0.222  # 로봇 IP
export ROS_DOMAIN_ID=27
ros2 launch turtlebot3_bringup robot.launch.py


터미널 2: 자율주행 실행 (우분투 PC)
export ROS_DOMAIN_ID=27
export TURTLEBOT3_MODEL=waffle_pi
source ~/my_ws/install/setup.bash
# 우리가 만든 통합 런치 실행 (위치추정+내비게이션+RViz)
ros2 launch my_bot tb3_localization.launch.py


🕹️ 4단계: RViz 조작 (실제 움직이기)
런치 파일이 켜지고 RViz 창이 뜨면 다음 마우스 조작을 진행합니다.

위치 초기화 (2D Pose Estimate)

-상단 메뉴의 2D Pose Estimate 아이콘 클릭.

-지도 위 로봇의 실제 위치를 클릭 후, 로봇이 바라보는 방향으로 드래그.

-체크: 초록색 화살표(파티클)들이 로봇 주변으로 삭 모이는지 확인.

목적지 설정 (Nav2 Goal)

-중요: 2D Pose 잡고 약 5~10초 정도 서버가 활성화될 때까지 대기.

-상단 메뉴의 Nav2 Goal 아이콘 클릭.

-로봇이 가야 할 경기장 안의 목적지를 클릭 후 드래그.

체크: 지도에 경로가 그려지면서 로봇이 출발하면 성공!
