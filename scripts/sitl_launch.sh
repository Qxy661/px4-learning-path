#!/bin/bash
# sitl_launch.sh — SITL 启动脚本
# 支持多种仿真器和机型

set -e

# 默认参数
SIMULATOR="gz"
MODEL="x500"
WORLD="default"
HEADLESS=false
INSTANCES=1

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --sim)
            SIMULATOR="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --world)
            WORLD="$2"
            shift 2
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --multi)
            INSTANCES="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查 PX4 目录
PX4_DIR="$HOME/PX4-Autopilot"
if [ ! -d "$PX4_DIR" ]; then
    echo "错误: PX4 目录不存在: $PX4_DIR"
    echo "请先运行 setup_px4.sh"
    exit 1
fi

cd "$PX4_DIR"

# 设置环境变量
if [ "$HEADLESS" = true ]; then
    export PX4_SIM_HEADLESS=1
fi

export PX4_GZ_WORLD="$WORLD"

# 构建目标
TARGET="px4_sitl"

case $SIMULATOR in
    gz|gazebo)
        TARGET="${TARGET} gz_${MODEL}"
        ;;
    jmavsim)
        TARGET="${TARGET} jmavsim"
        ;;
    *)
        echo "不支持的仿真器: $SIMULATOR"
        echo "支持: gz, gazebo, jmavsim"
        exit 1
        ;;
esac

echo "========================================"
echo "启动 PX4 SITL"
echo "========================================"
echo "仿真器: $SIMULATOR"
echo "机型: $MODEL"
echo "世界: $WORLD"
echo "无头模式: $HEADLESS"
echo "实例数: $INSTANCES"
echo "========================================"

if [ "$INSTANCES" -gt 1 ]; then
    echo "启动 $INSTANCES 个实例..."
    Tools/simulation/gz/multi_vehicle/launch_sitl.sh "$INSTANCES"
else
    echo "启动单机..."
    make $TARGET
fi
