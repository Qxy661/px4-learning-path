# 04 — 源码阅读指南

> 目标: 理解PX4核心模块的代码结构, 学会追踪控制链路

---

## 1. 代码目录结构

```
PX4-Autopilot/
├── src/
│   ├── modules/          # 核心模块
│   │   ├── ekf2/         # 状态估计器
│   │   ├── commander/    # 状态机
│   │   ├── navigator/    # 导航器
│   │   ├── mc_pos_control/  # 位置控制
│   │   ├── mc_att_control/  # 姿态控制
│   │   ├── control_allocator/  # 控制分配
│   │   └── logger/       # 日志
│   ├── drivers/          # 传感器驱动
│   ├── lib/              # 公共库
│   └── platforms/        # 平台层
├── msg/                  # uORB 消息定义
├── boards/               # 板级支持
├── ROMFS/                # 启动脚本
└── Tools/                # 工具
```

---

## 2. 追踪数据流

### 2.1 传感器 → EKF2

**关键文件**: `src/modules/ekf2/EKF/ekf.cpp`

```cpp
// EKF2 主循环
void Ekf::predict(const imuSample &imu_delayed)
{
    // 状态预测
    _state.quat_nominal = _state.quat_nominal * dq;
    _state.vel += delta_vel_earth;
    _state.pos += _state.vel * imu_dt;
}

// 观测更新
void Ekf::fuseBaro()
{
    // 气压计高度融合
    float innovation = _state.pos(2) - _baro_buffer.get_oldest().hgt;
}
```

**uORB 消息**:
- 输入: `sensor_accel`, `sensor_gyro`, `sensor_mag`, `sensor_baro`, `sensor_gps`
- 输出: `vehicle_attitude`, `vehicle_local_position`, `vehicle_global_position`

### 2.2 EKF2 → Commander

**关键文件**: `src/modules/commander/Commander.cpp`

```cpp
// 状态机主循环
void Commander::run()
{
    // 检查 EKF2 状态
    check_ekf_status();
    
    // 检查解锁条件
    prearm_check();
    
    // 处理模式切换
    handle_mode_switch();
}
```

**uORB 消息**:
- 输入: `vehicle_attitude`, `vehicle_local_position`, `estimator_status`
- 输出: `vehicle_status`, `commander_state`

### 2.3 Commander → Navigator

**关键文件**: `src/modules/navigator/Navigator.cpp`

```cpp
// 导航器主循环
void Navigator::run()
{
    // 根据飞行模式生成目标点
    switch (_vstatus.nav_state) {
        case vehicle_status_s::NAVIGATION_STATE_AUTO_MISSION:
            _mission.update();
            break;
        case vehicle_status_s::NAVIGATION_STATE_AUTO_RTL:
            _rtl.update();
            break;
    }
}
```

**uORB 消息**:
- 输入: `vehicle_status`, `vehicle_global_position`
- 输出: `position_setpoint_triplet`, `vehicle_command`

### 2.4 Navigator → 位置控制器

**关键文件**: `src/modules/mc_pos_control/MulticopterPositionControl.cpp`

```cpp
// 位置控制器主循环
void MulticopterPositionControl::run()
{
    // 获取目标点
    _position_setpoint_sub.update(&_pos_sp);
    
    // 位置环 → 期望速度
    Vector3f vel_sp = position_control();
    
    // 速度环 → 期望加速度
    Vector3f accel_sp = velocity_control(vel_sp);
    
    // 加速度 → 期望姿态+推力
    generate_attitude_setpoint(accel_sp);
}
```

**uORB 消息**:
- 输入: `vehicle_local_position`, `position_setpoint_triplet`
- 输出: `trajectory_setpoint`, `vehicle_attitude_setpoint`

### 2.5 位置控制器 → 姿态控制器

**关键文件**: `src/modules/mc_att_control/mc_att_control_main.cpp`

```cpp
// 姿态控制器主循环
void MulticopterAttitudeControl::run()
{
    // 获取期望姿态
    _att_sp_sub.update(&_att_sp);
    
    // 姿态环 → 期望角速率
    Vector3f rates_sp = attitude_control();
    
    // 角速率环 → 期望力矩
    Vector3f torque = rate_control(rates_sp);
    
    // 发布力矩
    publish_torque(torque);
}
```

**uORB 消息**:
- 输入: `vehicle_attitude`, `vehicle_attitude_setpoint`
- 输出: `vehicle_torque_setpoint`, `vehicle_thrust_setpoint`

### 2.6 姿态控制器 → 控制分配

**关键文件**: `src/modules/control_allocator/ControlAllocator.cpp`

```cpp
// 控制分配主循环
void ControlAllocator::run()
{
    // 获取期望力矩和推力
    _torque_sp_sub.update(&_torque_sp);
    _thrust_sp_sub.update(&_thrust_sp);
    
    // 力矩 → 电机输出
    allocate_actuators();
    
    // 发布执行器指令
    publish_actuator_motors();
}
```

**uORB 消息**:
- 输入: `vehicle_torque_setpoint`, `vehicle_thrust_setpoint`
- 输出: `actuator_motors`

---

## 3. uORB 消息详解

### 3.1 消息定义文件

位置: `msg/vehicle_local_position.msg`

```
uint64 timestamp          # 时间戳
float32 x                 # NED X (北)
float32 y                 # NED Y (东)
float32 z                 # NED Z (下)
float32 vx                # 速度 X
float32 vy                # 速度 Y
float32 vz                # 速度 Z
float32 ax                # 加速度 X
float32 ay                # 加速度 Y
float32 az                # 加速度 Z
bool xy_valid             # 水平位置有效
bool z_valid              # 垂直位置有效
bool v_xy_valid           # 水平速度有效
bool v_z_valid            # 垂直速度有效
```

### 3.2 消息发布/订阅

```cpp
// 订阅
uORB::Subscription _lpos_sub{ORB_ID(vehicle_local_position)};
vehicle_local_position_s _lpos;

if (_lpos_sub.update(&_lpos)) {
    // 数据已更新
    float x = _lpos.x;
    float y = _lpos.y;
    float z = _lpos.z;
}

// 发布
uORB::Publication<vehicle_attitude_s> _att_pub{ORB_ID(vehicle_attitude)};
vehicle_attitude_s att{};
att.timestamp = hrt_absolute_time();
att.q[0] = q.w();
att.q[1] = q.x();
att.q[2] = q.y();
att.q[3] = q.z();
_att_pub.publish(att);
```

---

## 4. 启动脚本

### 4.1 ROMFS 结构

```
ROMFS/px4fmu_common/
├── init.d/
│   ├── rcS              # 主启动脚本
│   ├── rc.mc_apps       # 多旋翼模块启动
│   ├── rc.fw_apps       # 固定翼模块启动
│   └── rc.sensors       # 传感器启动
└── mixers/
    ├── quad_x.main.mix  # 四旋翼混控器
    └── delta.main.mix   # 三角翼混控器
```

### 4.2 模块启动顺序

```bash
# rcS 中的启动顺序:
1. uORB (消息总线)
2. 传感器驱动 (IMU, 气压计, GPS)
3. EKF2 (状态估计)
4. Commander (状态机)
5. Navigator (导航器)
6. 位置/姿态控制器
7. 控制分配
8. MAVLink
```

---

## 5. 调试技巧

### 5.1 添加调试输出

```cpp
// 使用 PX4_INFO
PX4_INFO("Position: x=%.2f, y=%.2f, z=%.2f", x, y, z);

// 使用 PX4_WARN
PX4_WARN("EKF2 not converged!");

// 使用 PX4_ERR
PX4_ERR("Sensor read failed!");
```

### 5.2 使用 uORB 监听

```bash
# 在 px4> 中:

# 查看消息发布频率
uorb top

# 监听特定消息
listener vehicle_attitude

# 监听多次
listener vehicle_local_position -n 10
```

### 5.3 使用 gdb 调试

```bash
# 启动 gdb
gdb --args ./build/px4_sitl_default/bin/px4 -s etc/init.d-posix/rcS

# 设置断点
b MulticopterPositionControl::run

# 运行
run
```

---

## 6. 阅读建议

### 6.1 入门路线

```
1. 先理解 uORB 消息系统
2. 从传感器驱动开始, 理解数据如何产生
3. 追踪 EKF2 如何融合传感器数据
4. 理解 Commander 状态机
5. 最后看控制器代码
```

### 6.2 重点文件

| 文件 | 重要性 | 说明 |
|------|--------|------|
| `msg/*.msg` | ★★★★★ | 消息定义, 理解数据结构 |
| `modules/ekf2/` | ★★★★★ | 核心状态估计 |
| `modules/mc_pos_control/` | ★★★★ | 位置控制逻辑 |
| `modules/mc_att_control/` | ★★★★ | 姿态控制逻辑 |
| `modules/control_allocator/` | ★★★ | 控制分配 |
| `modules/commander/` | ★★★ | 状态机 |

---

## 下一步

→ [05 — 自定义模块开发](05-custom-module.md)
