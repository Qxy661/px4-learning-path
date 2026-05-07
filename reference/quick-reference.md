# PX4 快速参考卡

> 一页纸速查, 打印出来贴在工位上

---

## SITL 启动

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500          # Gazebo 四旋翼
make px4_sitl jmavsim          # jMAVSim (轻量)
HEADLESS=1 make px4_sitl gz_x500  # 无GUI
```

## px4> 控制台命令

```bash
commander takeoff               # 起飞
commander land                  # 降落
commander arm                   # 解锁
commander disarm                # 上锁
commander mode posctl           # 位置模式
commander mode offboard         # Offboard模式
commander mode auto:mission     # 航线模式
commander mode auto:rtl         # 返航
commander status                # 查看状态
```

## uORB 消息查看

```bash
uorb top                        # 消息频率总览
listener vehicle_attitude       # 监听姿态
listener vehicle_local_position # 监听位置
listener vehicle_status         # 监听状态
listener sensor_accel -n 5      # 监听加速度计(5次)
```

## 参数操作

```bash
param show MC_ROLLRATE_P        # 查看参数
param find MPC                  # 搜索参数
param set MC_ROLLRATE_P 0.15    # 设置参数
param save                      # 保存参数
```

## MAVLink 端口

| 端口 | 用途 |
|------|------|
| UDP 14550 | QGroundControl |
| UDP 14540 | Companion Computer |
| TCP 4560 | MAVSDK |

## PID 调参速查

```
调参顺序: 角速率环 → 姿态环 → 位置环

角速率环 (内环):
  MC_ROLLRATE_P   0.08-0.25   (振荡→减小, 迟钝→增大)
  MC_ROLLRATE_D   0.001-0.01  (抖动→减小)
  MC_ROLLRATE_I   0.1-0.5     (稳态误差→增大)

姿态环 (中环):
  MC_ROLL_P       4.0-8.0     (超调→减小)

位置环 (外环):
  MPC_XY_P        0.5-1.5     (跟踪慢→增大)
  MPC_XY_VEL_P    1.0-3.0     (响应刚度)
  MPC_Z_P         0.5-2.0     (高度跟踪)
```

## 关键参数速查

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `MC_ROLLRATE_P` | 0.15 | 滚转角速率P |
| `MC_PITCHRATE_P` | 0.15 | 俯仰角速率P |
| `MC_YAWRATE_P` | 0.2 | 偏航角速率P |
| `MC_ROLL_P` | 6.5 | 滚转角P |
| `MPC_XY_P` | 0.8 | 水平位置P |
| `MPC_Z_P` | 1.0 | 垂直位置P |
| `MPC_THR_HOVER` | 0.5 | 悬停油门 |
| `THR_MDL_FAC` | 0.0 | 推力模型系数 |
| `EKF2_GPS_CTRL` | 7 | GPS控制 |

## 坐标系

```
PX4 使用 NED (北东地):
  X = 北 (North)
  Y = 东 (East)
  Z = 地 (Down, 向下为正)

ROS2 使用 ENU (东北天):
  X = 东 (East)
  Y = 北 (North)
  Z = 天 (Up, 向上为正)

转换: NED[x,y,z] → ENU[y,x,-z]
```

## 数据流

```
传感器 → EKF2 → Commander → Navigator → 位置控制 → 姿态控制 → 控制分配 → 电机
```

## 日志分析

```bash
# 日志位置
~/PX4-Autopilot/build/px4_sitl_default/rootfs/fs/microsd/log/

# 关键日志字段
ATT     - 姿态 (roll/pitch/yaw)
LPSP    - 位置设定点
LPOS    - 本地位置
RATE    - 角速率
ACT     - 执行器输出
BAT     - 电池
```

## 故障排查

```
高频振荡 (10-20Hz) → 减小 MC_ROLLRATE_P/D
低频摆动 (1-5Hz)   → 减小 MC_ROLL_P
位置漂移           → 增大 MPC_XY_P
转弯掉高           → 增大 MPC_Z_VEL_I
GPS不锁定          → 移到室外, 等待2分钟
EKF不收敛          → 检查磁力计干扰
```
