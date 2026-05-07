# PX4 学习进度清单

> 每完成一项打勾, 追踪你的学习进度

---

## Week 1: 环境搭建 + 首次飞行

### 环境搭建
- [ ] WSL2 Ubuntu 22.04 安装成功
- [ ] PX4 代码克隆成功 (`--recursive`)
- [ ] 工具链安装完成 (`ubuntu.sh`)
- [ ] 首次编译成功 (`make px4_sitl_default`)
- [ ] Gazebo 仿真启动成功
- [ ] QGroundControl 连接成功

### 首次飞行
- [ ] 在 px4> 中起飞 (`commander takeoff`)
- [ ] 观察 Gazebo 中无人机悬停
- [ ] 降落 (`commander land`)
- [ ] 切换飞行模式 (`commander mode posctl`)
- [ ] 通过 QGroundControl 控制位置

---

## Week 2: 架构理解 + uORB

### 架构理解
- [ ] 理解 Flight Stack 分层
- [ ] 理解 Middleware (uORB + MAVLink)
- [ ] 理解 Platform Layer
- [ ] 能画出完整数据流图

### uORB 消息
- [ ] `uorb top` 查看消息频率
- [ ] `listener vehicle_attitude` 查看姿态
- [ ] `listener vehicle_local_position` 查看位置
- [ ] 理解消息发布/订阅机制
- [ ] 能说出 5 个关键消息的含义

---

## Week 3: SITL 深入 + QGroundControl

### SITL 使用
- [ ] 使用不同仿真器 (Gazebo/jMAVSim)
- [ ] 启动多机仿真
- [ ] 使用 Headless 模式
- [ ] 故障注入 (GPS丢失/传感器故障)
- [ ] 日志分析 (FlightPlot/pyulog)

### QGroundControl
- [ ] 航点任务规划
- [ ] 参数修改
- [ ] 传感器校准界面
- [ ] 飞行日志下载

---

## Week 4: PID 调参

### 理论
- [ ] 理解 P/I/D 各项作用
- [ ] 理解级联 PID 结构
- [ ] 理解从内环到外环调参顺序

### 实操
- [ ] 角速率环调参 (Roll Rate)
- [ ] 角速率环调参 (Pitch Rate)
- [ ] 角速率环调参 (Yaw Rate)
- [ ] 姿态环调参
- [ ] 位置环调参
- [ ] 推力模型调整 (`THR_MDL_FAC`)
- [ ] 使用 Autotune
- [ ] 参数文件导入/导出

---

## Week 5: 源码阅读

### 代码结构
- [ ] 理解 `src/modules/` 目录结构
- [ ] 理解 `msg/` 消息定义
- [ ] 理解 `ROMFS/` 启动脚本

### 核心模块
- [ ] 阅读 EKF2 核心代码
- [ ] 阅读 Commander 状态机
- [ ] 阅读位置控制器
- [ ] 阅读姿态控制器
- [ ] 阅读控制分配器
- [ ] 能追踪完整控制链路

### 调试
- [ ] 使用 `PX4_INFO` 添加调试输出
- [ ] 使用 gdb 调试 SITL
- [ ] 修改参数观察行为变化

---

## Week 6: 自定义模块开发

### Hello Sky
- [ ] 创建模块目录
- [ ] 编写 `CMakeLists.txt`
- [ ] 实现 `ModuleBase` 接口
- [ ] 编译并运行
- [ ] 查看输出

### 进阶模块
- [ ] 订阅 uORB 消息
- [ ] 发布 uORB 消息
- [ ] 定义自定义参数
- [ ] 使用工作队列
- [ ] 添加 MAVLink 命令

---

## Week 7: ROS2 集成

### 环境搭建
- [ ] ROS2 Humble 安装成功
- [ ] px4_msgs 编译成功
- [ ] Micro XRCE-DDS Agent 启动成功
- [ ] ROS2 能看到 PX4 话题

### Offboard 控制
- [ ] 基本 Offboard 节点运行
- [ ] 解锁 + 起飞
- [ ] 位置控制 (悬停)
- [ ] 圆形轨迹飞行
- [ ] 坐标系转换 (NED↔ENU)
- [ ] 自动降落

### MAVSDK
- [ ] MAVSDK 安装成功
- [ ] 基本连接测试
- [ ] 航点任务执行
- [ ] Offboard 模式控制

---

## Week 8: 实机部署

### 硬件准备
- [ ] Pixhawk 接线完成
- [ ] 电调连接正确
- [ ] GPS 安装正确
- [ ] 遥控器对频成功

### 固件和校准
- [ ] PX4 固件烧录成功
- [ ] 加速度计校准
- [ ] 磁力计校准
- [ ] 遥控器校准
- [ ] 电调校准
- [ ] 飞行模式配置
- [ ] 失控保护设置

### 首飞
- [ ] 起飞前检查清单完成
- [ ] 首次悬停成功
- [ ] 小幅度操控测试
- [ ] 降落并上锁
- [ ] 日志分析无异常

---

## 进阶技能

- [ ] 自定义混控器
- [ ] 故障检测和处理
- [ ] 避障集成
- [ ] 多机协调
- [ ] 提交 Issue/PR 到 PX4 社区
