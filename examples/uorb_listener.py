#!/usr/bin/env python3
"""
uORB 消息监听脚本

通过 Micro XRCE-DDS 监听 PX4 的 uORB 消息

运行方式:
  终端1: make px4_sitl gz_x500
  终端2: MicroXRCEAgent udp4 -p 8888
  终端3: python3 uorb_listener.py
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import (
    VehicleAttitude,
    VehicleLocalPosition,
    VehicleStatus,
    SensorCombined,
    BatteryStatus,
    EstimatorStatus,
)

import numpy as np


class UorbListener(Node):
    def __init__(self):
        super().__init__('uorb_listener')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # 订阅多个 uORB 消息
        self.att_sub = self.create_subscription(
            VehicleAttitude, '/fmu/out/vehicle_attitude',
            self.att_callback, qos_profile)

        self.lpos_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self.lpos_callback, qos_profile)

        self.status_sub = self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status',
            self.status_callback, qos_profile)

        self.battery_sub = self.create_subscription(
            BatteryStatus, '/fmu/out/battery_status',
            self.battery_callback, qos_profile)

        # 定时输出 (1Hz)
        self.timer = self.create_timer(1.0, self.print_status)

        # 状态
        self.attitude = None
        self.local_pos = None
        self.vehicle_status = None
        self.battery = None

        self.get_logger().info('uORB Listener 已启动, 正在监听消息...')

    def att_callback(self, msg):
        self.attitude = msg

    def lpos_callback(self, msg):
        self.local_pos = msg

    def status_callback(self, msg):
        self.vehicle_status = msg

    def battery_callback(self, msg):
        self.battery = msg

    def print_status(self):
        """每秒打印状态"""
        print("\033[2J\033[H")  # 清屏
        print("=" * 60)
        print("PX4 uORB 消息监听器")
        print("=" * 60)

        # 姿态
        if self.attitude is not None:
            q = self.attitude.q
            # 四元数转欧拉角
            roll = np.arctan2(2*(q[0]*q[1] + q[2]*q[3]), 1 - 2*(q[1]**2 + q[2]**2))
            pitch = np.arcsin(2*(q[0]*q[2] - q[3]*q[1]))
            yaw = np.arctan2(2*(q[0]*q[3] + q[1]*q[2]), 1 - 2*(q[2]**2 + q[3]**2))

            print(f"\n姿态 (Attitude):")
            print(f"  Roll:  {np.degrees(roll):+7.1f}°")
            print(f"  Pitch: {np.degrees(pitch):+7.1f}°")
            print(f"  Yaw:   {np.degrees(yaw):+7.1f}°")
        else:
            print("\n姿态: 等待数据...")

        # 位置
        if self.local_pos is not None:
            print(f"\n位置 (Local Position, NED):")
            print(f"  X (北): {self.local_pos.x:+8.2f} m")
            print(f"  Y (东): {self.local_pos.y:+8.2f} m")
            print(f"  Z (地): {self.local_pos.z:+8.2f} m")
            print(f"  高度:   {-self.local_pos.z:+8.2f} m")

            if self.local_pos.v_xy_valid:
                vx = self.local_pos.vx
                vy = self.local_pos.vy
                speed = np.sqrt(vx**2 + vy**2)
                print(f"  速度:   {speed:.2f} m/s (vx={vx:.2f}, vy={vy:.2f})")
        else:
            print("\n位置: 等待数据...")

        # 飞行状态
        if self.vehicle_status is not None:
            state_map = {
                0: "未初始化",
                1: "上锁",
                2: "待机",
                3: "待机 (手动)",
                4: "待机 (自动)",
                5: "手动",
                6: "稳定",
                7: "高度",
                8: "位置",
                9: "自动航线",
                10: "自动盘旋",
                11: "自动返航",
                14: "Offboard",
            }
            state = state_map.get(self.vehicle_status.nav_state, "未知")
            armed = "已解锁" if self.vehicle_status.arming_state == 2 else "已上锁"

            print(f"\n飞行状态:")
            print(f"  模式: {state}")
            print(f"  解锁: {armed}")
        else:
            print("\n飞行状态: 等待数据...")

        # 电池
        if self.battery is not None:
            voltage = self.battery.voltage_v
            current = self.battery.current_a
            remaining = self.battery.remaining * 100

            print(f"\n电池:")
            print(f"  电压: {voltage:.2f} V")
            print(f"  电流: {current:.2f} A")
            print(f"  剩余: {remaining:.0f}%")
        else:
            print("\n电池: 等待数据...")

        print("\n" + "=" * 60)
        print("按 Ctrl+C 退出")


def main(args=None):
    rclpy.init(args=args)
    node = UorbListener()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
