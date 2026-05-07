#!/bin/bash
# PX4 SITL 快速演示脚本
# 用法: bash sitl_demo.sh [gazebo|jmavsim]

SIM=${1:-gazebo}

echo "========================================="
echo "  PX4 SITL 演示"
echo "  仿真器: $SIM"
echo "========================================="

cd ~/PX4-Autopilot

case $SIM in
    gazebo)
        echo "启动 Gazebo + PX4 SITL..."
        make px4_sitl gz_x500
        ;;
    jmavsim)
        echo "启动 jMAVSim + PX4 SITL..."
        make px4_sitl jmavsim
        ;;
    *)
        echo "未知仿真器: $SIM (可选: gazebo, jmavsim)"
        exit 1
        ;;
esac
