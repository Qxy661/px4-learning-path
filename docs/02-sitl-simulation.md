# 02 — SITL 仿真深入

> 目标: 掌握PX4 SITL仿真的完整使用方法, 包括Gazebo场景配置、多机仿真、日志分析

---

## 1. SITL 架构

### 1.1 什么是SITL

SITL (Software In The Loop) = 纯软件仿真, 无需硬件:
```
┌──────────────┐     UDP      ┌──────────────┐
│   PX4 SITL   │ ←──────────→ │   Gazebo     │
│  (飞控代码)   │  MAVLink     │  (物理仿真)   │
└──────┬───────┘              └──────────────┘
       │ UDP 14550
       ▼
┌──────────────┐
│ QGroundControl│
│  (地面站)     │
└──────────────┘
```

### 1.2 支持的仿真器

| 仿真器 | 命令 | 特点 |
|--------|------|------|
| Gazebo Classic | `make px4_sitl gazebo-classic` | 旧版, 社区资源多 |
| Gazebo (Ignition) | `make px4_sitl gz_x500` | **推荐**, 新一代 |
| jMAVSim | `make px4_sitl jmavsim` | 轻量, 不需GPU |
| AirSim | `make px4_sitl airsim` | 高保真渲染 |
| FlightGear | `make px4_sitl flightgear` | 飞行仪表 |

---

## 2. Gazebo 仿真

### 2.1 启动标准四旋翼

```bash
cd ~/PX4-Autopilot

# 启动 X500 四旋翼 + Gazebo
make px4_sitl gz_x500
```

启动后:
- PX4 控制台出现 `px4>` 提示符
- Gazebo 窗口弹出, 显示四旋翼模型
- 自动启动 MAVLink UDP 14550 端口

### 2.2 可用机型

```bash
# 查看所有支持的目标
make list_config_targets | grep sitl

# 常用机型:
# gz_x500      - 四旋翼 (默认)
# gz_x500_depth - 带深度相机
# gz_standard_vtol - 标准VTOL
# gz_plane     - 固定翼
# gz_rover     - 车辆
```

### 2.3 自定义世界

```bash
# 使用空旷世界 (无建筑物)
make px4_sitl gz_x500_none

# 使用仓库世界
make px4_sitl gz_x500_warehouse

# 使用自定义世界
PX4_GZ_WORLD=my_world make px4_sitl gz_x500
```

世界文件位置: `Tools/simulation/gz/worlds/`

### 2.4 添加传感器

在 Gazebo 模型 SDF 文件中添加传感器:

```xml
<!-- 添加相机 -->
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image><width>640</width><height>480</height></image>
    <clip><near>0.1</near><far>100</far></clip>
  </camera>
  <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
    <render_engine>ogre2</render_engine>
  </plugin>
</sensor>
```

---

## 3. 基本飞行操作

### 3.1 解锁和起飞

在 `px4>` 提示符中:

```bash
# 查看状态
commander status

# 解锁 (arm)
commander arm

# 起飞到2.5米
commander takeoff

# 切换到位置模式
commander mode posctl

# 降落
commander land

# 上锁
commander disarm
```

### 3.2 飞行模式

| 模式 | 说明 | 命令 |
|------|------|------|
| Manual | 手动 (角速率) | `commander mode manual` |
| Stabilized | 姿态稳定 | `commander mode stabilized` |
| Altitude | 高度保持 | `commander mode altctl` |
| Position | 位置保持 | `commander mode posctl` |
| Mission | 自动航线 | `commander mode auto:mission` |
| Loiter | 盘旋 | `commander mode auto:loiter` |
| RTL | 返航 | `commander mode auto:rtl` |
| Offboard | 外部控制 | `commander mode offboard` |

### 3.3 航点任务

```bash
# 加载航点文件
param set MIS_DONE_BEHAV 0

# 使用 MAVLink 上传航点 (通过 QGroundControl)
# 或手动创建 mission 文件:
cat > /tmp/mission.txt << EOF
QGC WPL 110
0	1	0	16	0	0	0	0	47.397742	8.545594	50	1
1	0	3	16	0	0	0	0	47.397836	8.545689	50	1
2	0	3	16	0	0	0	0	47.397930	8.545784	50	1
EOF

# 通过 MAVProxy 上传
mavproxy.py --master=udp:127.0.0.1:14550
wp load /tmp/mission.txt
```

---

## 4. MAVLink 通信

### 4.1 端口配置

| 端口 | 用途 | 说明 |
|------|------|------|
| UDP 14550 | QGroundControl | 自动连接 |
| UDP 14540 | Companion Computer | 机载电脑 |
| TCP 4560 | MAVSDK | SDK 连接 |
| UDP 14580 | 多机第2架 | 实例1 |
| UDP 14560 | 多机第3架 | 实例2 |

### 4.2 MAVProxy 调试

```bash
# 安装
pip3 install mavproxy

# 连接
mavproxy.py --master=udp:127.0.0.1:14550

# 常用命令:
param show SYS_AUTOSTART    # 查看参数
param set SYS_AUTOSTART 4010  # 设置参数
wp list                      # 查看航点
status                       # 查看状态
mode guided                   # 切换模式
```

### 4.3 MAVSDK 连接

```python
from mavsdk import System
import asyncio

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("连接成功!")
            break
    
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
    await drone.action.land()

asyncio.run(main())
```

---

## 5. 多机仿真

### 5.1 启动多机

```bash
# 设置实例数
export PX4_SIM_MODEL=gz_x500
export PX4_SIM_WORLD=default

# 启动3架无人机
Tools/simulation/gz/multi_vehicle/launch_sitl.sh 3
```

### 5.2 多机端口分配

| 实例 | MAVLink UDP | Gazebo |
|------|-------------|--------|
| 0 | 14550 | 默认 |
| 1 | 14560 | +1 |
| 2 | 14570 | +2 |

### 5.3 多机通信

每架飞机有独立的:
- PX4 实例
- MAVLink 端口
- uORB 消息空间
- 参数空间

通过 MAVLink 的 `target_system` 区分不同飞机。

---

## 6. 日志分析

### 6.1 飞行日志

日志自动保存在:
```
~/PX4-Autopilot/build/px4_sitl_default/rootfs/fs/microsd/log/
```

### 6.2 使用 FlightPlot 分析

```bash
# 下载 FlightPlot
wget https://github.com/Dronecode/FlightPlot/releases/latest/download/FlightPlot.jar
java -jar FlightPlot.jar
```

关键图表:
- **ATT** - 姿态 (roll/pitch/yaw)
- **LPSP** - 本地位置设定点
- **LPOS** - 本地位置
- **RATE** - 角速率
- **ACT** - 执行器输出
- **BAT** - 电池

### 6.3 使用 pyulog 解析

```bash
pip3 install pyulog

# 转换为 CSV
ulog2csv flight.ulg

# 查看消息
ulog_info flight.ulg

# 查看特定消息
ulog_params flight.ulg
```

```python
from pyulog import ULog

ulog = ULog('flight.ulg')

# 获取姿态数据
att = ulog.get_dataset('vehicle_attitude')
roll = att.data['roll[0]']
pitch = att.data['roll[1]']
yaw = att.data['roll[2]']

# 获取位置数据
lpos = ulog.get_dataset('vehicle_local_position')
x = lpos.data['x']
y = lpos.data['y']
z = lpos.data['z']
```

---

## 7. 性能调优

### 7.1 仿真速度

```bash
# 查看实时因子
px4> listener simulator_status

# 调整仿真步长
param set SIM_RATE_HZ 400  # 默认400Hz
```

### 7.2 减少延迟

```bash
# 禁用不需要的模块
param set SENS_EN_TFMINI 0
param set SENS_EN_SF1XX 0

# 减少日志频率
param set SDLOG_PROFILE 1  # 最小日志
```

### 7.3 Headless 模式

```bash
# 无 GUI (CI/测试)
HEADLESS=1 make px4_sitl gz_x500

# 或设置环境变量
export PX4_SIM_HEADLESS=1
make px4_sitl gz_x500
```

---

## 8. 故障注入

### 8.1 传感器故障

```bash
# 模拟 GPS 丢失
param set EKF2_GPS_CTRL 0

# 模拟气压计故障
param set EKF2_BARO_CTRL 0

# 模拟磁力计故障
param set EKF2_MAG_TYPE 0
```

### 8.2 通信故障

```bash
# 断开遥控器 (触发 failsafe)
# 在 MAVProxy 中:
set heartbeat_lost 1
```

### 8.3 电机故障

```bash
# 在 Gazebo 中:
# 右键电机 → Disable Motor
```

---

## 9. 实验练习

### 练习 1: 基本飞行

```bash
# 1. 启动仿真
make px4_sitl gz_x500

# 2. 在 px4> 中:
commander takeoff
# 等待起飞完成

commander mode posctl
# 用 QGroundControl 拖动位置

commander land
```

### 练习 2: 航点任务

1. 启动仿真
2. 打开 QGroundControl
3. Plan View → 添加航点
4. Upload → Start Mission

### 练习 3: 日志分析

```bash
# 1. 执行一次飞行
commander takeoff
sleep 10
commander land

# 2. 找到日志文件
ls ~/PX4-Autopilot/build/px4_sitl_default/rootfs/fs/microsd/log/

# 3. 用 FlightPlot 分析
# 观察: 高度曲线、姿态曲线、电机输出
```

---

## 下一步

→ [03 — 参数调优](03-parameter-tuning.md)
