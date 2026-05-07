# 四旋翼 SITL 快速入门

> 10 分钟完成首次仿真飞行

---

## 1. 启动 SITL

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

等待:
- `px4>` 提示符出现
- Gazebo 窗口弹出, 显示四旋翼

## 2. 起飞

在 `px4>` 中:

```bash
commander takeoff
```

观察 Gazebo 中无人机上升到约 2.5m 悬停。

## 3. 查看状态

```bash
# 飞行状态
commander status

# 姿态
listener vehicle_attitude

# 位置
listener vehicle_local_position
```

## 4. 切换模式

```bash
# 切换到位置控制模式
commander mode posctl
```

在 QGroundControl 中:
1. 连接 UDP 14550
2. 拖动地图上的飞机图标
3. 观察飞机跟随移动

## 5. 降落

```bash
commander land
```

## 6. 航点任务

1. 打开 QGroundControl
2. 点击 Plan View
3. 在地图上点击添加航点
4. 设置高度 (建议 10-20m)
5. 点击 Upload
6. 切换到 Mission 模式:
```bash
commander mode auto:mission
```

## 7. 下一步

- 阅读 [01 — PX4 架构解析](01-architecture.md) 理解原理
- 阅读 [03 — 参数调优](03-parameter-tuning.md) 学习调参
- 尝试 [offboard_circle.py](../examples/offboard_circle.py) ROS2 控制
