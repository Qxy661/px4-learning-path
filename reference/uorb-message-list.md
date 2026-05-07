# 常用 uORB 消息列表

> PX4 模块间通信的核心消息, 按功能分类

---

## 传感器消息

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `sensor_accel` | 加速度计 | `x`, `y`, `z`, `temperature` |
| `sensor_gyro` | 陀螺仪 | `x`, `y`, `z`, `temperature` |
| `sensor_mag` | 磁力计 | `x`, `y`, `z` |
| `sensor_baro` | 气压计 | `pressure`, `temperature`, `altitude` |
| `sensor_gps` | GPS | `lat`, `lon`, `alt`, `eph`, `epv`, `satellites_used` |
| `distance_sensor` | 测距仪 | `current_distance`, `orientation` |
| `sensor_optical_flow` | 光流 | `pixel_flow_x`, `pixel_flow_y`, `quality` |

---

## 状态估计消息

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `vehicle_attitude` | 姿态四元数 | `q[4]` (w,x,y,z) |
| `vehicle_local_position` | 本地位置 (NED) | `x`, `y`, `z`, `vx`, `vy`, `vz` |
| `vehicle_global_position` | GPS 位置 | `lat`, `lon`, `alt`, `eph`, `epv` |
| `estimator_status` | 估计器状态 | `filter_fault_flags`, `solution_status` |
| `ekf2_timestamps` | EKF2 时间戳 | `timestamp` |

---

## 控制消息

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `vehicle_attitude_setpoint` | 期望姿态 | `q_d[4]`, `thrust_body[3]` |
| `vehicle_rates_setpoint` | 期望角速率 | `roll`, `pitch`, `yaw` |
| `trajectory_setpoint` | 期望轨迹 | `position[3]`, `velocity[3]`, `yaw` |
| `vehicle_thrust_setpoint` | 期望推力 | `xyz[3]` |
| `vehicle_torque_setpoint` | 期望力矩 | `xyz[3]` |
| `actuator_motors` | 电机输出 | `control[4]` (0-1) |
| `actuator_servos` | 舵面输出 | `control[4]` (-1 到 1) |

---

## 状态和模式消息

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `vehicle_status` | 飞行状态 | `nav_state`, `arming_state`, `vehicle_type` |
| `commander_state` | Commander 状态 | `state_machine` |
| `offboard_control_mode` | Offboard 模式 | `position`, `velocity`, `attitude` |
| `vehicle_command` | 命令 | `command`, `param1-7` |
| `vehicle_command_ack` | 命令确认 | `command`, `result` |

---

## 任务消息

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `mission_result` | 任务结果 | `finished`, `success`, `seq_current` |
| `position_setpoint_triplet` | 航点三元组 | `previous`, `current`, `next` |
| `vehicle_roi` | 关注点 | `mode`, `x`, `y`, `z` |

---

## 电池和电源

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `battery_status` | 电池状态 | `voltage_v`, `current_a`, `remaining` |
| `power_monitor` | 功率监控 | `voltage_v`, `current_a`, `power_w` |

---

## MAVLink 消息

| 消息名 | 说明 | 关键字段 |
|--------|------|----------|
| `mavlink_log` | MAVLink 日志 | `text`, `severity` |
| `transponder_report` | 应答机 | `ICAO_address`, `lat`, `lon`, `altitude` |

---

## 消息使用示例

### 订阅消息

```cpp
#include <uORB/topics/vehicle_attitude.h>

uORB::Subscription att_sub{ORB_ID(vehicle_attitude)};
vehicle_attitude_s att{};

if (att_sub.update(&att)) {
    float roll = att.q[0];  // 四元数 w
    float pitch = att.q[1]; // 四元数 x
}
```

### 发布消息

```cpp
#include <uORB/Publication.hpp>
#include <uORB/topics/trajectory_setpoint.h>

uORB::Publication<trajectory_setpoint_s> sp_pub{ORB_ID(trajectory_setpoint)};
trajectory_setpoint_s sp{};
sp.timestamp = hrt_absolute_time();
sp.position[0] = 0.0f;  // x
sp.position[1] = 0.0f;  // y
sp.position[2] = -5.0f; // z (NED, 向下为正)
sp_pub.publish(sp);
```

### 在 px4> 中监听

```bash
# 查看消息频率
uorb top

# 监听消息
listener vehicle_attitude

# 监听多次
listener vehicle_local_position -n 10
```

---

## 消息频率参考

| 消息 | 典型频率 | 说明 |
|------|----------|------|
| `sensor_accel` | 250-800 Hz | IMU |
| `sensor_gyro` | 250-800 Hz | IMU |
| `vehicle_attitude` | 250 Hz | EKF2 输出 |
| `vehicle_local_position` | 50-100 Hz | EKF2 输出 |
| `actuator_motors` | 400 Hz | 控制输出 |
| `vehicle_status` | 10 Hz | 状态 |
| `battery_status` | 1 Hz | 电池 |
