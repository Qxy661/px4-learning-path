#!/usr/bin/env python3
"""
ROS2 Offboard 圆形轨迹控制示例

使用 PX4 + ROS2 + Micro XRCE-DDS 控制无人机飞圆形轨迹

运行方式:
  终端1: make px4_sitl gz_x500
  终端2: MicroXRCEAgent udp4 -p 8888
  终端3: python3 offboard_circle.py
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

import numpy as np


class OffboardCircle(Node):
    def __init__(self):
        super().__init__('offboard_circle')

        # QoS 配置 (PX4 要求 BEST_EFFORT + TRANSIENT_LOCAL)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # 发布者
        self.offboard_control_mode_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_setpoint_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        # 订阅者
        self.vehicle_local_position_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self.vehicle_local_position_callback, qos_profile)

        # 状态
        self.offboard_setpoint_counter = 0
        self.vehicle_local_position = None

        # 圆形轨迹参数
        self.radius = 5.0   # 半径 [m]
        self.omega = 0.3    # 角速度 [rad/s]
        self.height = -5.0  # 高度 [m] (NED, 向下为正)
        self.t = 0.0

        # 定时器 (20Hz)
        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info('Offboard Circle 节点已启动')

    def vehicle_local_position_callback(self, msg):
        self.vehicle_local_position = msg

    def arm(self):
        """解锁电机"""
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
        self.get_logger().info('Arm command sent')

    def disarm(self):
        """上锁电机"""
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=0.0)
        self.get_logger().info('Disarm command sent')

    def engage_offboard_mode(self):
        """切换到 Offboard 模式"""
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0)
        self.get_logger().info('Offboard mode command sent')

    def land(self):
        """降落"""
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
        self.get_logger().info('Land command sent')

    def publish_vehicle_command(self, command, **params):
        """发布 MAVLink 命令"""
        msg = VehicleCommand()
        msg.param1 = params.get("param1", 0.0)
        msg.param2 = params.get("param2", 0.0)
        msg.param3 = params.get("param3", 0.0)
        msg.param4 = params.get("param4", 0.0)
        msg.param5 = params.get("param5", 0.0)
        msg.param6 = params.get("param6", 0.0)
        msg.param7 = params.get("param7", 0.0)
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)

    def publish_offboard_control_heartbeat(self):
        """发布 Offboard 心跳 (必须 2Hz 以上)"""
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_control_mode_pub.publish(msg)

    def publish_trajectory_setpoint(self, x, y, z, yaw):
        """发布轨迹目标点"""
        msg = TrajectorySetpoint()
        msg.position = [float(x), float(y), float(z)]
        msg.yaw = float(yaw)
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_setpoint_pub.publish(msg)

    def timer_callback(self):
        """定时回调 (20Hz)"""
        # 发送心跳
        self.publish_offboard_control_heartbeat()

        # 前 10 个周期只发心跳, 然后切换模式并解锁
        if self.offboard_setpoint_counter == 10:
            self.engage_offboard_mode()
            self.arm()

        if self.vehicle_local_position is not None:
            # 计算圆形轨迹
            x = self.radius * np.cos(self.omega * self.t)
            y = self.radius * np.sin(self.omega * self.t)
            z = self.height
            yaw = self.omega * self.t + np.pi / 2  # 朝向切线方向

            self.publish_trajectory_setpoint(x, y, z, yaw)
            self.t += 0.05

            # 输出当前位置 (每 2 秒)
            if int(self.t * 20) % 40 == 0:
                pos = self.vehicle_local_position
                self.get_logger().info(
                    f'位置: x={pos.x:.1f}, y={pos.y:.1f}, z={pos.z:.1f} | '
                    f'目标: x={x:.1f}, y={y:.1f}, z={z:.1f}'
                )

        if self.offboard_setpoint_counter < 11:
            self.offboard_setpoint_counter += 1


def main(args=None):
    rclpy.init(args=args)
    offboard_circle = OffboardCircle()

    try:
        rclpy.spin(offboard_circle)
    except KeyboardInterrupt:
        offboard_circle.get_logger().info('用户中断, 降落中...')
        offboard_circle.land()
    finally:
        offboard_circle.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
