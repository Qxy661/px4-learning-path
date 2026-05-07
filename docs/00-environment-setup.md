# 00 — 环境搭建

> 目标: 在WSL2 Ubuntu上搭建PX4开发环境, 完成首次SITL仿真飞行

---

## 1. 安装WSL2

在Windows终端(PowerShell管理员)中执行:

```powershell
wsl --install -d Ubuntu-22.04
```

重启后设置用户名和密码。

验证:
```bash
wsl --list --verbose
# 应显示 Ubuntu-22.04 Running 2
```

---

## 2. 安装PX4工具链

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git cmake build-essential genromfs \
    python3-pip python3-venv ninja-build

# 克隆PX4 (必须用 --recursive!)
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot

# 运行官方安装脚本
bash Tools/setup/ubuntu.sh

# 重新加载环境变量
source ~/.bashrc
```

**关键点**: `--recursive` 会拉取所有子模块, 不加的话EKF2等核心库会缺失。

---

## 3. 首次编译

```bash
cd ~/PX4-Autopilot

# 编译四旋翼SITL目标
make px4_sitl_default
```

编译成功标志: 看到 `[100%] Built target px4` 

编译时间: 首次约10-20分钟, 后续增量编译约1-2分钟。

---

## 4. 启动SITL仿真

### 4.1 Gazebo (推荐, 3D可视化)

```bash
make px4_sitl gz_x500
```

成功标志: 
- `px4>` 提示符出现
- Gazebo窗口弹出, 显示四旋翼模型

### 4.2 jMAVSim (轻量, 不需要GPU)

```bash
make px4_sitl jmavsim
```

### 4.3 无GUI模式 (CI/测试用)

```bash
HEADLESS=1 make px4_sitl gz_x500
```

---

## 5. 验证飞行

在 `px4>` 提示符中:

```
# 查看当前状态
commander status

# 起飞
commander takeoff

# 等待几秒, 观察Gazebo中无人机起飞

# 降落
commander land
```

---

## 6. 安装QGroundControl

```bash
# Ubuntu安装
sudo usermod -a -G dialout $USER
sudo apt-get remove modemmanager -y
sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav -y

# 下载AppImage
wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage
chmod +x QGroundControl.AppImage
./QGroundControl.AppImage
```

QGC会自动发现SITL的UDP端口14550。

---

## 7. 安装MAVProxy (可选, 调试用)

```bash
pip3 install mavproxy

# 连接到SITL
mavproxy.py --master=udp:127.0.0.1:14550
```

---

## 常见问题

### Q: `make` 报错找不到子模块
```bash
# 解决: 重新拉取子模块
cd ~/PX4-Autopilot
git submodule update --init --recursive
```

### Q: Gazebo窗口不弹出
```bash
# 检查WSLg是否启用
echo $DISPLAY
# 应该输出类似 :0 的值

# 如果为空, 更新WSL2
wsl --update
```

### Q: 起飞后翻车
默认参数可能不适合你的仿真环境。先继续学习, 后面调参章节会解决。

### Q: 编译内存不足
```bash
# 减少并行编译数
make px4_sitl_default -j2
```

---

## 下一步

→ [01 — PX4架构解析](01-architecture.md)
