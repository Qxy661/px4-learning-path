# PX4 飞控学习路径 — 从零到能改代码

> 面向飞控方向学生/工程师的系统化学习指南
> 基于 PX4 官方文档, 结合实操经验, 覆盖从环境搭建到实机部署全流程

---

## 你将学到什么

- PX4 架构原理 (uORB消息总线、模块化设计)
- SITL 仿真环境 (Gazebo/jMAVSim)
- PID 调参方法论 (内环→外环、Autotune)
- 控制链路追踪 (传感器→EKF→控制器→混控→电机)
- 自定义模块开发 (Hello Sky → 自己的模块)
- ROS2 Offboard 控制 (uXRCE-DDS 桥接)
- 实机部署流程 (Pixhawk 烧录→校准→首飞)

---

## 学习路线 (建议8周)

```
Week 1: 环境搭建 + 首次SITL飞行
Week 2: 架构理解 + uORB消息系统
Week 3: SITL深入 + QGroundControl
Week 4: PID调参方法论
Week 5: 源码阅读 + 控制链路
Week 6: 自定义模块开发
Week 7: ROS2集成 + Offboard控制
Week 8: 实机部署 + 首飞
```

---

## 项目结构

```
px4-learning-path/
├── README.md                          # 本文件
├── docs/                              # 学习文档
│   ├── 00-environment-setup.md        # 环境搭建
│   ├── 01-architecture.md             # PX4架构解析
│   ├── 02-sitl-simulation.md          # SITL仿真
│   ├── 03-parameter-tuning.md         # 参数调优
│   ├── 04-code-reading.md             # 源码阅读指南
│   ├── 05-custom-module.md            # 自定义模块
│   ├── 06-ros2-integration.md         # ROS2集成
│   ├── 07-hardware-deploy.md          # 实机部署
│   └── 08-common-pitfalls.md          # 常见坑
├── examples/                          # 示例代码
│   ├── offboard_circle.py             # ROS2圆形轨迹
│   ├── offboard_land.py               # ROS2自动降落
│   ├── mavlink_test.py                # MAVLink通信测试
│   └── uorb_listener.py               # uORB消息监听
├── scripts/                           # 工具脚本
│   ├── setup_px4.sh                   # 一键环境搭建
│   ├── sitl_launch.sh                 # SITL启动脚本
│   └── param_template.parm            # 调参模板
└── reference/                         # 参考资料
    ├── px4-architecture.png           # 架构图
    ├── uorb-message-list.md           # 常用uORB消息
    └── tuning-checklist.md            # 调参检查清单
```

---

## 快速开始

```bash
# 1. 克隆本项目
git clone https://github.com/YOUR_USERNAME/px4-learning-path.git

# 2. 搭建PX4环境 (参考 docs/00-environment-setup.md)
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash Tools/setup/ubuntu.sh

# 3. 首次SITL飞行
make px4_sitl gz_x500
# 在 px4> 提示符中:
commander takeoff

# 4. 开始学习
# 按 docs/ 顺序阅读
```

---

## 前置要求

- Ubuntu 22.04 (推荐WSL2)
- 基础C++知识
- 基础Python知识 (ROS2示例需要)
- 了解PID控制基本概念
- 了解坐标系和旋转矩阵

---

## 参考资源

| 资源 | 链接 |
|------|------|
| PX4官方文档 | https://docs.px4.io/main/en/ |
| PX4 GitHub | https://github.com/PX4/PX4-Autopilot |
| PX4 Dev Guide | https://dev.px4.io/ |
| PX4 论坛 | https://discuss.px4.io/ |
| QGroundControl | https://docs.qgroundcontrol.com/ |
| MAVSDK | https://mavsdk.mavlink.io/ |
| ROS2+PX4 | https://docs.px4.io/main/en/ros2/ |

---

## License

MIT
