#!/usr/bin/env python3
"""
ROS2 Offboard 自动降落示例

演示如何使用 Offboard 模式控制无人机降落

运行方式:
  终端1: make px4_sitl gz_x500
  终端2: MicroXRCEAgent udp4 -p 8888
  终端3: python3 offboard_land.py
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
)


class OffboardLand(Node):
    def __init__(self):
        super().__init__('offboard_land')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.offboard_control_mode_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_setpoint_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        self.vehicle_local_position_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self.vehicle_local_position_callback, qos_profile)

        self.offboard_setpoint_counter = 0
        self.vehicle_local_position = None
        self.state = 'TAKEOFF'  # TAKEOFF -> HOVER -> LAND -> DONE
        self.hover_time = 0.0

        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info('Offboard Land 节点已启动')

    def vehicle_local_position_callback(self, msg):
        self.vehicle_local_position = msg

    def arm(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
        self.get_logger().info('Arm')

    def engage_offboard_mode(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0)
        self.get_logger().info('Offboard mode')

    def land(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
        self.get_logger().info('Land command sent')

    def publish_vehicle_command(self, command, **params):
        msg = VehicleCommand()
        msg.param1 = params.get("param1", 0.0)
        msg.param2 = params.get("param2", 0.0)
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)

    def publish_offboard_control_heartbeat(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_control_mode_pub.publish(msg)

    def publish_trajectory_setpoint(self, x, y, z, yaw=0.0):
        msg = TrajectorySetpoint()
        msg.position = [float(x), float(y), float(z)]
        msg.yaw = float(yaw)
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_setpoint_pub.publish(msg)

    def timer_callback(self):
        self.publish_offboard_control_heartbeat()

        if self.offboard_setpoint_counter == 10:
            self.engage_offboard_mode()
            self.arm()

        if self.vehicle_local_position is not None:
            alt = -self.vehicle_local_position.z  # NED -> 高度

            if self.state == 'TAKEOFF':
                # 起飞到 5m
                self.publish_trajectory_setpoint(0.0, 0.0, -5.0)
                if alt > 4.5:
                    self.state = 'HOVER'
                    self.get_logger().info('到达目标高度, 开始悬停')

            elif self.state == 'HOVER':
                # 悬停 5 秒
                self.publish_trajectory_setpoint(0.0, 0.0, -5.0)
                self.hover_time += 0.05
                if self.hover_time > 5.0:
                    self.state = 'LAND'
                    self.get_logger().info('悬停完成, 开始降落')

            elif self.state == 'LAND':
                # 缓慢降落
                target_z = -alt * 0.5  # 逐渐降低目标
                if alt < 0.3:
                    self.publish_vehicle_command(
                        VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=0.0)
                    self.state = 'DONE'
                    self.get_logger().info('已着陆并上锁')
                else:
                    self.publish_trajectory_setpoint(0.0, 0.0, target_z)

        if self.offboard_setpoint_counter < 11:
            self.offboard_setpoint_counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = OffboardLand()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('用户中断')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
