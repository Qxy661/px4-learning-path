# 01 — PX4 架构解析

> 目标: 理解PX4的分层架构、模块设计、消息通信机制

---

## 1. 两层架构

PX4分为两个主要层次:

```
┌─────────────────────────────────────────────────┐
│                Flight Stack                      │
│  传感器融合 → 状态估计 → 导航 → 控制 → 执行     │
├─────────────────────────────────────────────────┤
│                Middleware                        │
│  uORB消息总线 + MAVLink通信 + DDS桥接           │
├─────────────────────────────────────────────────┤
│                Platform Layer                    │
│  硬件驱动 + RTOS + 板级支持                      │
└─────────────────────────────────────────────────┘
```

---

## 2. Flight Stack 模块

### 2.1 传感器驱动 (Drivers)

位置: `src/drivers/`

| 驱动 | 作用 | 发布的消息 |
|------|------|-----------|
| IMU | 加速度计+陀螺仪 | `sensor_accel`, `sensor_gyro` |
| Barometer | 气压计 | `sensor_baro` |
| GPS | GPS接收机 | `sensor_gps` |
| Magnetometer | 磁力计 | `sensor_mag` |
| DistanceSensor | 测距仪 | `distance_sensor` |

### 2.2 状态估计 (EKF2)

位置: `src/modules/ekf2/`

EKF2 是PX4的核心, 融合多传感器数据输出状态估计:

```
输入:
  - sensor_accel (加速度)
  - sensor_gyro (角速度)
  - sensor_mag (磁场)
  - sensor_baro (气压高度)
  - sensor_gps (GPS位置)
  - optical_flow (光流)

输出:
  - vehicle_attitude (姿态四元数)
  - vehicle_local_position (本地位置NED)
  - vehicle_global_position (GPS位置)
  - estimator_status (估计器状态)
```

### 2.3 Commander (状态机)

位置: `src/modules/commander/`

管理飞行状态和模式切换:
- 解锁/上锁 (Arm/Disarm)
- 飞行模式切换 (Manual/Altitude/Position/Auto/Offboard)
- 故障检测和处理 (GPS丢失、电池低、遥控器丢失)

### 2.4 Navigator (导航器)

位置: `src/modules/navigator/`

根据飞行模式生成目标点:
- Mission模式: 按航点飞行
- RTL模式: 返航点
- Loiter模式: 盘旋
- Offboard模式: 外部目标

### 2.5 位置控制器

位置: `src/modules/mc_pos_control/` (四旋翼)

```
输入: vehicle_local_position + trajectory_setpoint
输出: trajectory_setpoint (期望姿态+推力)
```

### 2.6 姿态控制器

位置: `src/modules/mc_att_control/`

```
输入: vehicle_attitude + trajectory_setpoint
输出: actuator_motors (期望力矩)
```

### 2.7 Control Allocation (控制分配)

位置: `src/modules/control_allocator/`

PX4 v1.14+ 引入, 替代旧的mixer模块:
```
输入: 期望力矩 + 期望推力
输出: 各电机PWM值
```

---

## 3. uORB 消息系统

### 3.1 什么是uORB

uORB (micro Object Request Broker) 是PX4的发布/订阅消息总线:
- 模块间解耦通信
- 支持多订阅者
- 非阻塞读写
- DDS兼容 (可桥接到ROS2)

### 3.2 消息定义

消息定义在 `msg/` 目录:

```bash
# 查看所有消息类型
ls msg/

# 查看某个消息定义
cat msg/vehicle_local_position.msg
```

消息格式示例 (`vehicle_attitude.msg`):
```
uint64 timestamp          # 时间戳 (微秒)
float32[4] q              # 姿态四元数 [w,x,y,z]
float32[3] delta_q_reset  # 四元数重置增量
uint8 quat_reset_counter  # 四元数重置计数器
```

### 3.3 实操: 查看uORB消息

```bash
# 启动SITL
make px4_sitl gz_x500

# 在 px4> 提示符中:

# 查看消息发布频率
uorb top

# 监听特定消息
listener vehicle_attitude

# 监听并持续更新
listener vehicle_local_position -n 10
```

---

## 4. MAVLink 通信

### 4.1 MAVLink是什么

MAVLink是地面站(GCS)与飞控之间的通信协议:
- 轻量级二进制协议
- 支持命令、遥测、参数
- PX4支持MAVLink v2

### 4.2 MAVLink端口

| 端口 | 用途 |
|------|------|
| UDP 14550 | QGroundControl |
| UDP 14540 | Companion Computer |
| TCP 4560 | MAVSDK |

### 4.3 实操: MAVLink通信

```bash
# 用MAVProxy连接
mavproxy.py --master=udp:127.0.0.1:14550

# 查看消息
status
wp list
param show SYS_AUTOSTART
```

---

## 5. 数据流总结

```
传感器驱动
    ↓ sensor_accel, sensor_gyro, sensor_mag, sensor_baro, sensor_gps
EKF2
    ↓ vehicle_attitude, vehicle_local_position, vehicle_global_position
Commander + Navigator
    ↓ trajectory_setpoint
Position Controller
    ↓ trajectory_setpoint (姿态+推力)
Attitude Controller
    ↓ actuator_motors
Control Allocation
    ↓ actuator_motors (PWM)
电机驱动
    ↓ 电机转速
```

---

## 6. 关键概念

### 6.1 坐标系

PX4使用NED坐标系:
- X: 北 (North)
- Y: 东 (East)
- Z: 下 (Down)

注意: 与ROS2的ENU(东北天)不同!

### 6.2 时间系统

- 所有时间戳: 微秒 (uint64)
- 来自 `hrt_absolute_time()`

### 6.3 参数系统

- 存储在EEPROM/Flash
- 通过MAVLink可远程读写
- QGroundControl可图形化修改

---

## 下一步

→ [02 — SITL仿真](02-sitl-simulation.md)
