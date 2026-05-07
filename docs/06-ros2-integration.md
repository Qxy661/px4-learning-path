# 06 — ROS2 集成

> 目标: 掌握PX4与ROS2的集成方法, 实现Offboard控制

---

## 1. 架构概览

### 1.1 PX4 + ROS2 通信

```
┌──────────────┐     uXRCE-DDS     ┌──────────────┐
│    PX4       │ ←───────────────→ │   ROS2       │
│   (uORB)     │                   │   (DDS)      │
└──────────────┘                   └──────────────┘
```

uXRCE-DDS 是 PX4 和 ROS2 之间的桥梁:
- PX4 的 uORB 消息 ↔ ROS2 的 DDS 消息
- 双向通信, 低延迟
- 支持发布/订阅模式

### 1.2 消息映射

| PX4 uORB | ROS2 Topic | 类型 |
|----------|------------|------|
| `vehicle_attitude` | `/fmu/out/vehicle_attitude` | px4_msgs/msg/VehicleAttitude |
| `vehicle_local_position` | `/fmu/out/vehicle_local_position` | px4_msgs/msg/VehicleLocalPosition |
| `trajectory_setpoint` | `/fmu/in/trajectory_setpoint` | px4_msgs/msg/TrajectorySetpoint |
| `offboard_control_mode` | `/fmu/in/offboard_control_mode` | px4_msgs/msg/OffboardControlMode |

---

## 2. 环境搭建

### 2.1 安装 ROS2 Humble

```bash
# 设置源
sudo apt update && sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 安装 ROS2
sudo apt update
sudo apt install -y ros-humble-desktop python3-colcon-common-extensions

# 设置环境
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2.2 安装 px4_msgs

```bash
mkdir -p ~/px4_ros2_ws/src
cd ~/px4_ros2_ws/src

# 克隆 px4_msgs
git clone https://github.com/PX4/px4_msgs.git -b release/1.14

# 编译
cd ~/px4_ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 2.3 安装 Micro XRCE-DDS Agent

```bash
# 安装 Fast-DDS
sudo apt install -y ros-humble-rmw-fastrtps-cpp

# 安装 Micro XRCE-DDS Agent
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig /usr/local/lib/
```

---

## 3. 启动 PX4 + ROS2

### 3.1 启动顺序

```bash
# 终端 1: 启动 PX4 SITL
cd ~/PX4-Autopilot
make px4_sitl gz_x500

# 终端 2: 启动 Micro XRCE-DDS Agent
MicroXRCEAgent udp4 -p 8888

# 终端 3: 启动 ROS2 节点
source ~/px4_ros2_ws/install/setup.bash
ros2 run my_package my_node
```

### 3.2 验证连接

```bash
# 查看 ROS2 话题
ros2 topic list

# 应该看到:
# /fmu/out/vehicle_attitude
# /fmu/out/vehicle_local_position
# /fmu/in/offboard_control_mode
# ...
```

---

## 4. ROS2 Offboard 控制示例

### 4.1 基本 Offboard 节点

**offboard_control.py**:

```python
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
    VehicleAttitude
)

import numpy as np
from scipy.spatial.transform import Rotation


class OffboardControl(Node):
    def __init__(self):
        super().__init__('offboard_control')
        
        # QoS 配置
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # 发布者
        self.offboard_control_mode_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_setpoint_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', qos_profile)
        
        # 订阅者
        self.vehicle_local_position_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self.vehicle_local_position_callback, qos_profile)
        
        # 状态
        self.offboard_setpoint_counter = 0
        self.vehicle_local_position = None
        
        # 定时器 (20Hz)
        self.timer = self.create_timer(0.05, self.timer_callback)
    
    def vehicle_local_position_callback(self, msg):
        self.vehicle_local_position = msg
    
    def arm(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
        self.get_logger().info('Arm command sent')
    
    def disarm(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=0.0)
        self.get_logger().info('Disarm command sent')
    
    def engage_offboard_mode(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0)
        self.get_logger().info('Offboard mode command sent')
    
    def land(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
        self.get_logger().info('Land command sent')
    
    def publish_vehicle_command(self, command, **params):
        msg = VehicleCommand()
        msg.param1 = params.get("param1", 0.0)
        msg.param2 = params.get("param2", 0.0)
        msg.param3 = params.get("param3", 0.0)
        msg.param4 = params.get("param4", 0.0)
        msg.param5 = params.get("param5", 0.0)
        msg.param6 = params.get("param6", 0.0)
        msg.param7 = params.get("param7", 0.0)
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)
    
    def publish_offboard_control_heartbeat(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_control_mode_pub.publish(msg)
    
    def publish_trajectory_setpoint(self, x, y, z, yaw):
        msg = TrajectorySetpoint()
        msg.position = [x, y, z]
        msg.yaw = yaw
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_setpoint_pub.publish(msg)
    
    def timer_callback(self):
        # 发送心跳
        self.publish_offboard_control_heartbeat()
        
        if self.offboard_setpoint_counter == 10:
            self.engage_offboard_mode()
            self.arm()
        
        if self.vehicle_local_position is not None:
            # 悬停在 [0, 0, -5] (NED 坐标系, Z 轴向下为正)
            self.publish_trajectory_setpoint(0.0, 0.0, -5.0, 0.0)
        
        if self.offboard_setpoint_counter < 11:
            self.offboard_setpoint_counter += 1


def main(args=None):
    rclpy.init(args=args)
    offboard_control = OffboardControl()
    rclpy.spin(offboard_control)
    offboard_control.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 4.2 运行

```bash
# 终端 1: PX4 SITL
make px4_sitl gz_x500

# 终端 2: Micro XRCE-DDS Agent
MicroXRCEAgent udp4 -p 8888

# 终端 3: ROS2 节点
python3 offboard_control.py
```

---

## 5. 坐标系转换

### 5.1 NED vs ENU

PX4 使用 NED (北东地), ROS2 使用 ENU (东北天):

```python
def ned_to_enu(ned):
    """NED → ENU"""
    return [ned[1], ned[0], -ned[2]]

def enu_to_ned(enu):
    """ENU → NED"""
    return [enu[1], enu[0], -enu[2]]
```

### 5.2 姿态转换

```python
from scipy.spatial.transform import Rotation

def px4_quat_to_ros(px4_quat):
    """PX4 四元数 [w,x,y,z] → ROS 四元数 [x,y,z,w]"""
    return [px4_quat[1], px4_quat[2], px4_quat[3], px4_quat[0]]

def ros_quat_to_px4(ros_quat):
    """ROS 四元数 [x,y,z,w] → PX4 四元数 [w,x,y,z]"""
    return [ros_quat[3], ros_quat[0], ros_quat[1], ros_quat[2]]
```

---

## 6. 圆形轨迹示例

```python
import numpy as np

class CircleTrajectory(OffboardControl):
    def __init__(self):
        super().__init__()
        self.radius = 5.0  # 半径 [m]
        self.omega = 0.3   # 角速度 [rad/s]
        self.height = -5.0 # 高度 [m] (NED)
        self.t = 0.0
    
    def timer_callback(self):
        self.publish_offboard_control_heartbeat()
        
        if self.offboard_setpoint_counter == 10:
            self.engage_offboard_mode()
            self.arm()
        
        if self.vehicle_local_position is not None:
            # 圆形轨迹
            x = self.radius * np.cos(self.omega * self.t)
            y = self.radius * np.sin(self.omega * self.t)
            z = self.height
            yaw = self.omega * self.t + np.pi / 2
            
            self.publish_trajectory_setpoint(x, y, z, yaw)
            self.t += 0.05
        
        if self.offboard_setpoint_counter < 11:
            self.offboard_setpoint_counter += 1
```

---

## 7. MAVSDK (Python)

### 7.1 安装

```bash
pip3 install mavsdk
```

### 7.2 基本示例

```python
import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    print("等待连接...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("已连接!")
            break
    
    print("解锁...")
    await drone.action.arm()
    
    print("起飞...")
    await drone.action.takeoff()
    await asyncio.sleep(5)
    
    print("飞到目标点...")
    await drone.action.goto_location(47.398039, 8.545572, 500, 0)
    await asyncio.sleep(10)
    
    print("降落...")
    await drone.action.land()

asyncio.run(main())
```

### 7.3 Offboard 模式 (MAVSDK)

```python
async def offboard_example():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
    
    # 启动 Offboard
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, -5.0, 0.0))
    await drone.offboard.start()
    
    # 飞圆形
    import math
    for i in range(100):
        angle = i * 0.1
        x = 5.0 * math.cos(angle)
        y = 5.0 * math.sin(angle)
        await drone.offboard.set_position_ned(
            PositionNedYaw(x, y, -5.0, 0.0))
        await asyncio.sleep(0.1)
    
    await drone.offboard.stop()
    await drone.action.land()
```

---

## 8. 常见问题

### Q: 无法连接 Micro XRCE-DDS Agent

```bash
# 检查 PX4 参数
param show XRCE_DDS_CFG
# 应该是 TELEM2 或 UDP

# 检查端口
MicroXRCEAgent udp4 -p 8888
```

### Q: ROS2 话题为空

```bash
# 检查 PX4 中的 DDS 状态
uxrce_dds status

# 检查 ROS2 节点
ros2 node list
ros2 topic info /fmu/out/vehicle_attitude
```

### Q: NED/ENU 坐标搞混

```python
# PX4: NED (北东地)
# ROS2: ENU (东北天)
# Z 轴符号相反!
```

---

## 下一步

→ [07 — 实机部署](07-hardware-deploy.md)
