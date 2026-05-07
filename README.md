# PX4 飞控学习路径 — 从零到能改代码

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PX4](https://img.shields.io/badge/PX4-v1.14+-blue.svg)](https://github.com/PX4/PX4-Autopilot)
[![ROS2](https://img.shields.io/badge/ROS2-Humble-green.svg)](https://docs.ros.org/en/humble/)

> 面向飞控方向学生/工程师的系统化学习指南
> 基于 PX4 官方文档, 结合实操经验, 覆盖从环境搭建到实机部署全流程

---

## PX4 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                   │
│   QGroundControl · MAVSDK · ROS2 Offboard · 自定义模块          │
├─────────────────────────────────────────────────────────────────┤
│                       Flight Stack                               │
│  ┌──────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 传感器   │→│ EKF2 │→│ Commander│→│ Navigator│→│ 位置控制 │  │
│  │ 驱动    │ │ 状态  │ │ 状态机   │ │ 导航器   │ │ 位置环   │  │
│  └──────────┘ │ 估计  │ └──────────┘ └──────────┘ └────┬─────┘  │
│               └──────┘                                  │        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │        │
│  │ 电机    │←│ 控制    │←│ 姿态    │←──────────────┘        │
│  │ 驱动    │ │ 分配    │ │ 控制    │                          │
│  └──────────┘ └──────────┘ └──────────┘                          │
├─────────────────────────────────────────────────────────────────┤
│                       Middleware                                  │
│         uORB 消息总线 · MAVLink · uXRCE-DDS (ROS2)             │
├─────────────────────────────────────────────────────────────────┤
│                     Platform Layer                               │
│           硬件驱动 · NuttX RTOS · 板级支持 (Pixhawk)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 你将学到什么

| 技能 | 内容 |
|------|------|
| 架构原理 | uORB消息总线、模块化设计、数据流 |
| SITL仿真 | Gazebo/jMAVSim、多机仿真、故障注入 |
| PID调参 | 内环→外环、Autotune、推力模型 |
| 控制链路 | 传感器→EKF→控制器→混控→电机 |
| 模块开发 | Hello Sky→自定义模块→参数→工作队列 |
| ROS2集成 | uXRCE-DDS、px4_msgs、Offboard控制 |
| 实机部署 | Pixhawk烧录→校准→首飞→日志分析 |

---

## 学习路线 (建议8周)

```
Week 1 ─→ 环境搭建 + 首次SITL飞行 ──────────── docs/00-environment-setup.md
Week 2 ─→ 架构理解 + uORB消息系统 ──────────── docs/01-architecture.md
Week 3 ─→ SITL深入 + QGroundControl ────────── docs/02-sitl-simulation.md
Week 4 ─→ PID调参方法论 ────────────────────── docs/03-parameter-tuning.md
Week 5 ─→ 源码阅读 + 控制链路 ──────────────── docs/04-code-reading.md
Week 6 ─→ 自定义模块开发 ──────────────────── docs/05-custom-module.md
Week 7 ─→ ROS2集成 + Offboard控制 ─────────── docs/06-ros2-integration.md
Week 8 ─→ 实机部署 + 首飞 ─────────────────── docs/07-hardware-deploy.md
```

---

## 快速开始

```bash
# 1. 克隆本项目
git clone https://github.com/Qxy661/px4-learning-path.git

# 2. 搭建PX4环境
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash Tools/setup/ubuntu.sh
source ~/.bashrc

# 3. 首次SITL飞行
make px4_sitl gz_x500
# 在 px4> 提示符中:
commander takeoff

# 4. 开始学习
# 按 docs/ 顺序阅读, 使用 docs/learning-checklist.md 追踪进度
```

---

## 项目结构

```
px4-learning-path/
├── README.md                          ← 你在这里
├── LICENSE
├── docs/                              # 学习文档
│   ├── 00-environment-setup.md        # 环境搭建
│   ├── 01-architecture.md             # PX4架构解析
│   ├── 02-sitl-simulation.md          # SITL仿真
│   ├── 03-parameter-tuning.md         # 参数调优
│   ├── 04-code-reading.md             # 源码阅读指南
│   ├── 05-custom-module.md            # 自定义模块
│   ├── 06-ros2-integration.md         # ROS2集成
│   ├── 07-hardware-deploy.md          # 实机部署
│   ├── 08-common-pitfalls.md          # 常见坑
│   ├── learning-checklist.md          # 学习进度清单
│   └── tutorial_quad.md               # 四旋翼快速入门
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
    ├── quick-reference.md             # 快速参考卡
    ├── uorb-message-list.md           # 常用uORB消息
    └── tuning-checklist.md            # 调参检查清单
```

---

## 前置要求

| 要求 | 说明 |
|------|------|
| 系统 | Ubuntu 22.04 (推荐WSL2) |
| C++ | 基础知识 (能读懂类和函数) |
| Python | 基础知识 (ROS2示例需要) |
| 控制 | 了解PID基本概念 |
| 数学 | 了解坐标系和旋转矩阵 |

---

## 与 ArduPilot 对比

| 方面 | PX4 | ArduPilot |
|------|-----|-----------|
| 消息系统 | uORB (发布/订阅) | 直接函数调用 |
| 构建系统 | CMake | waf |
| 脚本 | C++ 模块 | Lua |
| 地面站 | QGroundControl | Mission Planner |
| SITL | `make px4_sitl` | `sim_vehicle.py` |
| ROS2 | uXRCE-DDS | MAVROS |
| 优势 | 架构清晰, 现代化 | 生态丰富, 社区大 |

> 如果你也学 ArduPilot, 看 [ardupilot-learning-path](https://github.com/Qxy661/ardupilot-learning-path)

---

## 参考资源

| 资源 | 链接 |
|------|------|
| PX4 官方文档 | https://docs.px4.io/main/en/ |
| PX4 GitHub | https://github.com/PX4/PX4-Autopilot |
| PX4 Dev Guide | https://dev.px4.io/ |
| PX4 论坛 | https://discuss.px4.io/ |
| QGroundControl | https://docs.qgroundcontrol.com/ |
| MAVSDK | https://mavsdk.mavlink.io/ |
| ROS2+PX4 | https://docs.px4.io/main/en/ros2/ |

---

## License

MIT - 详见 [LICENSE](LICENSE)
