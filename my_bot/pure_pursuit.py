import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from math import pow, atan2, sqrt, sin, pi


class PurePursuit(Node):
    def __init__(self):
        super().__init__('pure_pursuit_node')

        '''
            teacher:
            how to calculate angular velocity?
            linear_velocity * (2 * sin(diff_to_target_angle) / lookahead_distance)
        '''

        self.lookahead_distance = 0.5
        self.linear_velocity = 0.2
        self.goal_tolerance = 0.2

        # path 파라미터 선언
        # 2차원 좌표를 평탄화(flatten)해서 받음: [x1, y1, x2, y2, ...]
        self.declare_parameter('path', [3.557, -0.168])

<<<<<<< HEAD
<<<<<<< HEAD
        self.lookahead_distance = 0.2 # 전방 주시 거리 (훈련생이 정하기)
        self.linear_velocity = 0.2 # linear.x 값 (훈련생이 정하기)     
        self.goal_tolerance = 0.2 # 목표와의 거리 허용 범위 (훈련생이 정하기)     

				# 목적지 좌표 : 내가 가고자 하는 곳의 좌표를 RViz에서 확인!
        self.path = [
            [1.5, 0.5]
            [1.8, 1.1]
        ]
=======
        # 파라미터 읽어서 self.path 초기화
        raw_path = self.get_parameter('path').value
        self.path = self.parse_path_parameter(raw_path)
>>>>>>> 83027aa302c80aeb8f8745eb5779ca5c4de7c318
=======
        # 초기 path 설정
        self.path = self.parse_path_parameter(
            self.get_parameter('path').value
        )
>>>>>>> 936abf44acf32a972a8f8f928a938ba71d04e2c4
        self.current_waypoint_index = 0

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscription_ = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.pose_callback,
            10
        )

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        self.is_localized = False

        # 동적 파라미터 변경 콜백 등록
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.timer = self.create_timer(0.5, self.control_loop)
        self.get_logger().info(f"Pure Pursuit Node Started! path={self.path}")
        self.get_logger().info("Waiting for AMCL pose...")

    def parse_path_parameter(self, flat_path):
        """
        [x1, y1, x2, y2, ...] 형태의 리스트를
        [[x1, y1], [x2, y2], ...] 형태로 변환
        """
        if len(flat_path) % 2 != 0:
            raise ValueError("path parameter length must be even. Example: [x1, y1, x2, y2]")

        parsed_path = []
        for i in range(0, len(flat_path), 2):
            parsed_path.append([float(flat_path[i]), float(flat_path[i + 1])])

        if len(parsed_path) == 0:
            raise ValueError("path parameter must contain at least one waypoint.")

        return parsed_path

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'path':
                try:
                    new_path = self.parse_path_parameter(param.value)
                    self.path = new_path
                    self.current_waypoint_index = 0

                    self.get_logger().info(f"Path updated: {self.path}")
                    self.get_logger().info("Restarting navigation from waypoint 0")

                except ValueError as e:
                    return SetParametersResult(
                        successful=False,
                        reason=str(e)
                    )

        return SetParametersResult(successful=True)

    def pose_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        self.current_yaw = atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )
        self.is_localized = True

    def control_loop(self):
        if not self.is_localized:
            return

        if self.current_waypoint_index >= len(self.path):
            self.stop_robot()
            return

        goal_x = self.path[self.current_waypoint_index][0]
        goal_y = self.path[self.current_waypoint_index][1]

        dx = goal_x - self.current_x
        dy = goal_y - self.current_y
        distance = sqrt(pow(dx, 2) + pow(dy, 2))

        if distance < self.goal_tolerance:
            self.get_logger().info(f"Waypoint {self.current_waypoint_index} Reached!")
            self.current_waypoint_index += 1
            return

        target_angle = atan2(dy, dx)
        alpha = target_angle - self.current_yaw

        if alpha > pi:
            alpha -= 2 * pi
        elif alpha < -pi:
            alpha += 2 * pi

        angular_velocity = self.linear_velocity * (2.0 * sin(alpha)) / self.lookahead_distance

        cmd = Twist()
        cmd.linear.x = self.linear_velocity
        cmd.angular.z = angular_velocity

        if cmd.angular.z > 1.0:
            cmd.angular.z = 1.0
        if cmd.angular.z < -1.0:
            cmd.angular.z = -1.0

        self.publisher_.publish(cmd)

    def stop_robot(self):
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.publisher_.publish(cmd)
        self.get_logger().info("All waypoints completed. Robot Stopped.")


def main(args=None):
    rclpy.init(args=args)
    node = PurePursuit()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()