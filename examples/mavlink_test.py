#!/usr/bin/env python3
"""
MAVLink 通信测试脚本

使用 MAVSDK 连接 PX4 SITL, 测试基本命令

运行方式:
  终端1: make px4_sitl gz_x500
  终端2: python3 mavlink_test.py
"""

import asyncio
from mavsdk import System
from mavsdk.offboard import PositionNedYaw
import math


async def connect():
    """连接到 PX4"""
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("等待连接...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"已连接: system_id={state}")
            break

    return drone


async def arm_and_takeoff(drone, altitude=5.0):
    """解锁并起飞"""
    print("解锁电机...")
    await drone.action.arm()

    print(f"起飞到 {altitude}m...")
    await drone.action.set_takeoff_altitude(altitude)
    await drone.action.takeoff()

    # 等待到达高度
    async for position in drone.telemetry.position():
        rel_alt = position.relative_altitude_m
        if rel_alt >= altitude * 0.9:
            print(f"到达高度: {rel_alt:.1f}m")
            break


async def fly_circle(drone, radius=5.0, height=5.0, duration=30.0):
    """飞圆形轨迹"""
    print(f"开始圆形轨迹: r={radius}m, h={height}m, t={duration}s")

    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, -height, 0.0))
    await drone.offboard.start()

    dt = 0.1
    steps = int(duration / dt)
    omega = 2 * math.pi / duration

    for i in range(steps):
        angle = omega * i * dt
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        yaw = math.degrees(angle + math.pi / 2)

        await drone.offboard.set_position_ned(
            PositionNedYaw(x, y, -height, yaw))

        if i % 50 == 0:
            print(f"  t={i*dt:.1f}s, pos=({x:.1f}, {y:.1f}, {-height})")

        await asyncio.sleep(dt)

    await drone.offboard.stop()
    print("圆形轨迹完成")


async def land(drone):
    """降落"""
    print("降落中...")
    await drone.action.land()

    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("已着陆")
            break


async def main():
    drone = await connect()

    try:
        await arm_and_takeoff(drone, altitude=5.0)
        await fly_circle(drone, radius=5.0, height=5.0, duration=30.0)
        await land(drone)
    except Exception as e:
        print(f"错误: {e}")
        print("尝试降落...")
        await drone.action.land()


if __name__ == '__main__':
    asyncio.run(main())
