# 08 — 常见问题与避坑指南

> 目标: 总结PX4学习和开发中的常见问题, 提供解决方案

---

## 1. 编译问题

### 1.1 子模块缺失

```bash
# 错误: fatal: not a tree object
# 或: error: pathspec 'xxx' did not match any file(s)

# 解决:
cd ~/PX4-Autopilot
git submodule update --init --recursive
```

### 1.2 编译内存不足

```bash
# 错误: c++: internal compiler error: Killed

# 解决: 减少并行编译数
make px4_sitl_default -j2
```

### 1.3 Python 版本问题

```bash
# 错误: SyntaxError: invalid syntax

# 解决: 使用 Python 3.8+
python3 --version
# 如果版本太低, 安装 Python 3.10
sudo apt install python3.10
```

### 1.4 Gazebo 启动失败

```bash
# 错误: [Err] [RenderEngine.cc:62] Unable to find rendering plugin

# 解决:
# 1. 检查显卡驱动
nvidia-smi

# 2. 更新 Gazebo
sudo apt update && sudo apt upgrade

# 3. 使用软件渲染
export LIBGL_ALWAYS_SOFTWARE=1
make px4_sitl gz_x500
```

---

## 2. SITL 问题

### 2.1 无法连接 QGroundControl

```bash
# 原因: 防火墙阻止 UDP 14550

# 解决:
sudo ufw allow 14550/udp
# 或关闭防火墙
sudo ufw disable
```

### 2.2 仿真速度慢

```bash
# 原因: CPU 性能不足

# 解决:
# 1. 使用 Headless 模式
HEADLESS=1 make px4_sitl gz_x500

# 2. 减少仿真频率
param set SIM_RATE_HZ 200
```

### 2.3 飞机翻车

```bash
# 原因: 默认参数不适合

# 解决:
# 1. 检查 EKF2 是否收敛
commander status

# 2. 手动调参
param set MC_ROLLRATE_P 0.1
param set MC_PITCHRATE_P 0.1
```

---

## 3. ROS2 集成问题

### 3.1 Micro XRCE-DDS 连接失败

```bash
# 错误: [ERROR] [MicroXRCEAgent]: create session failed...

# 解决:
# 1. 检查 PX4 参数
param show XRCE_DDS_CFG
# 应该是 TELEM2 或 UDP

# 2. 检查端口
MicroXRCEAgent udp4 -p 8888

# 3. 检查防火墙
sudo ufw allow 8888/udp
```

### 3.2 ROS2 话题为空

```bash
# 原因: PX4 未发布消息

# 解决:
# 1. 检查 PX4 中的 DDS 状态
uxrce_dds status

# 2. 检查 ROS2 节点
ros2 node list
ros2 topic info /fmu/out/vehicle_attitude

# 3. 检查 QoS 设置
ros2 topic echo /fmu/out/vehicle_attitude
```

### 3.3 坐标系混乱

```bash
# 问题: 飞机飞反方向

# 原因: NED/ENU 坐标搞混

# 解决:
# PX4: NED (北东地)
# ROS2: ENU (东北天)
# Z 轴符号相反!

def ned_to_enu(ned):
    return [ned[1], ned[0], -ned[2]]
```

---

## 4. PID 调参问题

### 4.1 高频振荡

```bash
# 现象: 电机声音尖锐, 飞机抖动

# 原因: 角速率环 P 或 D 太大

# 解决:
param set MC_ROLLRATE_P 0.1    # 减小
param set MC_ROLLRATE_D 0.002  # 减小
```

### 4.2 低频摆动

```bash
# 现象: 飞机缓慢摆动

# 原因: 姿态环 P 太大

# 解决:
param set MC_ROLL_P 5.0  # 减小
```

### 4.3 位置跟踪有稳态误差

```bash
# 现象: 飞机位置有偏差

# 原因: 速度环 I 不够

# 解决:
param set MPC_XY_VEL_I_ACC 0.4  # 增大
```

### 4.4 转弯时掉高

```bash
# 现象: 转弯时高度下降

# 原因: 垂直速度环 I 不够

# 解决:
param set MPC_Z_VEL_I_ACC 2.0  # 增大
```

---

## 5. 硬件问题

### 5.1 GPS 信号差

```bash
# 现象: GPS 长时间不锁定

# 原因:
# 1. 室内
# 2. 遮挡
# 3. GPS 模块故障

# 解决:
# 1. 移到室外
# 2. 等待 1-2 分钟
# 3. 检查 GPS 模块
```

### 5.2 电池电压下降快

```bash
# 现象: 飞行时间短

# 原因:
# 1. 电池老化
# 2. 电流过大
# 3. 螺旋桨不匹配

# 解决:
# 1. 更换电池
# 2. 检查电流
# 3. 更换合适的螺旋桨
```

### 5.3 电机过热

```bash
# 现象: 电机烫手

# 原因:
# 1. 螺旋桨太大
# 2. 电流过大
# 3. 电机故障

# 解决:
# 1. 更换合适的螺旋桨
# 2. 检查电流
# 3. 更换电机
```

---

## 6. 飞行问题

### 6.1 起飞后翻车

```bash
# 原因:
# 1. 螺旋桨装反
# 2. 电机转向错误
# 3. 电调未校准

# 解决:
# 1. 确认 CW/CCW
# 2. 确认电机转向
# 3. 重新校准电调
```

### 6.2 飞行中漂移

```bash
# 现象: 飞机缓慢漂移

# 原因:
# 1. 传感器未校准
# 2. GPS 信号差
# 3. PID 参数不合适

# 解决:
# 1. 重新校准传感器
# 2. 等待 GPS 锁定
# 3. 调整 PID 参数
```

### 6.3 遥控器无响应

```bash
# 原因:
# 1. 遥控器未对频
# 2. 通道映射错误
# 3. 接收机故障

# 解决:
# 1. 重新对频
# 2. 重新校准遥控器
# 3. 检查接收机
```

---

## 7. 日志分析问题

### 7.1 日志文件为空

```bash
# 原因: 日志未启动

# 解决:
# 1. 检查 SD 卡
# 2. 检查日志参数
param show SDLOG_MODE
# 应该是 1 (从解锁到上锁)
```

### 7.2 日志分析工具

```bash
# FlightPlot (推荐)
java -jar FlightPlot.jar

# pyulog
pip3 install pyulog
ulog2csv flight.ulg
```

### 7.3 关键日志字段

| 字段 | 说明 | 正常范围 |
|------|------|----------|
| ATT.roll | 滚转角 | ±5° (悬停) |
| ATT.pitch | 俯仰角 | ±5° (悬停) |
| RATE.roll | 滚转角速率 | ±100°/s |
| LPOS.x | 北向位置 | 航点位置 |
| LPOS.z | 高度 | 任务高度 |
| BAT.V | 电池电压 | > 14V (4S) |
| BAT.C | 电流 | < 50A |

---

## 8. 安全提醒

```
1. 首飞务必在空旷场地
2. 保持安全距离 (> 5m)
3. 随时准备切换手动模式
4. 电池低电量立即降落
5. 检查螺旋桨是否损坏
6. 不要在人群附近飞行
7. 遵守当地法规
8. 戴护目镜
```

---

## 9. 学习资源

| 资源 | 链接 | 说明 |
|------|------|------|
| PX4 官方文档 | https://docs.px4.io/main/en/ | 最权威 |
| PX4 论坛 | https://discuss.px4.io/ | 社区支持 |
| PX4 GitHub | https://github.com/PX4/PX4-Autopilot | 源码 |
| QGroundControl | https://docs.qgroundcontrol.com/ | 地面站 |
| MAVSDK | https://mavsdk.mavlink.io/ | SDK |
| ROS2+PX4 | https://docs.px4.io/main/en/ros2/ | ROS2 集成 |

---

## 10. 总结

```
学习 PX4 的关键:
1. 先理解架构, 再动手
2. 从 SITL 开始, 逐步到实机
3. 系统化调参, 不要盲目
4. 阅读源码, 理解原理
5. 多看日志, 多分析
6. 安全第一, 小心操作
```

---

## 完成!

恭喜你完成 PX4 飞控学习路径!

你现在应该能够:
- 理解 PX4 架构和数据流
- 使用 SITL 进行仿真
- 系统化调参
- 阅读和修改源码
- 集成 ROS2 进行 Offboard 控制
- 部署到实机

继续学习:
- 阅读 PX4 源码, 理解更多细节
- 参与社区, 提问和回答问题
- 开发自己的功能模块
- 探索更高级的主题 (避障、SLAM、集群)
