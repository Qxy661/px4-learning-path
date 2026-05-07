#!/bin/bash
# setup_px4.sh — PX4 一键环境搭建脚本
# 适用于 Ubuntu 22.04 (WSL2 或原生)

set -e

echo "========================================"
echo "PX4 开发环境一键搭建"
echo "========================================"

# 检查系统
if ! grep -q "Ubuntu 22.04" /etc/os-release; then
    echo "警告: 此脚本针对 Ubuntu 22.04, 其他版本可能需要调整"
fi

# 更新系统
echo "[1/6] 更新系统..."
sudo apt update && sudo apt upgrade -y

# 安装基础工具
echo "[2/6] 安装基础工具..."
sudo apt install -y \
    git cmake build-essential genromfs \
    python3-pip python3-venv ninja-build \
    ccache clang lld llvm \
    libxml2-dev libxml2-utils \
    xsltproc protobuf-compiler

# 克隆 PX4
echo "[3/6] 克隆 PX4 代码..."
if [ -d "$HOME/PX4-Autopilot" ]; then
    echo "PX4-Autopilot 目录已存在, 跳过克隆"
else
    cd ~
    git clone https://github.com/PX4/PX4-Autopilot.git --recursive
fi

# 运行官方安装脚本
echo "[4/6] 运行 PX4 安装脚本..."
cd ~/PX4-Autopilot
bash Tools/setup/ubuntu.sh

# 重新加载环境变量
echo "[5/6] 重新加载环境变量..."
source ~/.bashrc

# 首次编译
echo "[6/6] 首次编译 (可能需要 10-20 分钟)..."
make px4_sitl_default

echo ""
echo "========================================"
echo "PX4 环境搭建完成!"
echo "========================================"
echo ""
echo "启动 SITL 仿真:"
echo "  cd ~/PX4-Autopilot"
echo "  make px4_sitl gz_x500"
echo ""
echo "启动 jMAVSim (轻量, 不需 GPU):"
echo "  make px4_sitl jmavsim"
echo ""
