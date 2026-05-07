# 03 — 参数调优指南

> 目标: 掌握PX4 PID调参方法论, 从内环到外环系统化调参

---

## 1. PX4 参数系统

### 1.1 参数存储

- 存储在 EEPROM/Flash (掉电不丢失)
- 通过 MAVLink 远程读写
- QGroundControl 图形化修改
- 参数文件 `.param` 批量导入/导出

### 1.2 查看和修改参数

```bash
# 在 px4> 中:

# 查看所有参数 (搜索)
param find MC_ROLL

# 查看参数值
param show MC_ROLLRATE_P

# 修改参数
param set MC_ROLLRATE_P 0.15

# 保存参数
param save
```

### 1.3 参数分组

| 前缀 | 类别 | 示例 |
|------|------|------|
| `MC_` | 多旋翼控制 | `MC_ROLLRATE_P` |
| `FW_` | 固定翼控制 | `FW_ROLL_P` |
| `EKF2_` | 状态估计 | `EKF2_IMU_NOISE` |
| `MPC_` | 位置控制 | `MPC_XY_P` |
| `COM_` | Commander | `COM_ARM_EKF_AB` |
| `SYS_` | 系统 | `SYS_AUTOSTART` |
| `BAT_` | 电池 | `BAT_N_CELLS` |
| `SENS_` | 传感器 | `SENS_BARO_QNH` |

---

## 2. PID 调参方法论

### 2.1 调参原则

**核心规则**: 从内环到外环, 从P开始再加D, 最后加I

```
位置环 (外环)
    ↓ 期望姿态
姿态环 (中环)
    ↓ 期望角速率
角速率环 (内环)
    ↓ 电机输出
```

### 2.2 调参顺序

```
1. 角速率环 (ROLLRATE / PITCHRATE / YAWRATE)
   - 先调 P, 看响应速度
   - 再加 D, 抑制振荡
   - 最后加 I, 消除稳态误差

2. 姿态环 (ROLL / PITCH / YAW)
   - 只需调 P (PI 控制器)
   - 不要太大, 否则超调

3. 位置环 (MPC_XY / MPC_Z)
   - 位置 P 决定跟踪速度
   - 速度 P 决定响应刚度
```

---

## 3. 角速率环调参

### 3.1 关键参数

| 参数 | 默认值 | 作用 | 调参范围 |
|------|--------|------|----------|
| `MC_ROLLRATE_P` | 0.15 | 比例增益 | 0.08-0.25 |
| `MC_ROLLRATE_I` | 0.2 | 积分增益 | 0.1-0.5 |
| `MC_ROLLRATE_D` | 0.003 | 微分增益 | 0.001-0.01 |
| `MC_PITCHRATE_P` | 0.15 | 俯仰P | 同滚转 |
| `MC_YAWRATE_P` | 0.2 | 偏航P | 0.1-0.4 |
| `MC_YAWRATE_I` | 0.1 | 偏航I | 0.05-0.2 |

### 3.2 调参步骤

```bash
# Step 1: 设置安全参数
param set MC_ROLLRATE_P 0.1
param set MC_ROLLRATE_I 0
param set MC_ROLLRATE_D 0

# Step 2: 起飞悬停
commander takeoff

# Step 3: 观察日志 (用 QGroundControl)
# 如果振荡 → P 太大, 减小
# 如果响应慢 → P 太小, 增大

# Step 4: 加入 D (抑制振荡)
param set MC_ROLLRATE_D 0.003

# Step 5: 加入 I (消除稳态误差)
param set MC_ROLLRATE_I 0.2
```

### 3.3 调参技巧

**P 增益过大**: 高频振荡 (10-20Hz), 电机声音尖锐
**P 增益过小**: 响应迟钝, 位置跟踪差
**D 增益过大**: 低频抖动 (1-5Hz)
**D 增益过小**: 振荡衰减慢
**I 增益过大**: 低频大幅摆动
**I 增益过小**: 存在稳态误差

---

## 4. 姿态环调参

### 4.1 关键参数

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `MC_ROLL_P` | 6.5 | 滚转角P增益 |
| `MC_PITCH_P` | 6.5 | 俯仰角P增益 |
| `MC_YAW_P` | 2.8 | 偏航角P增益 |
| `MC_YAW_WEIGHT` | 0.4 | 偏航权重 |

### 4.2 调参方法

```bash
# 姿态环 P 通常不需要大幅调整
# 如果振荡: 减小 MC_ROLL_P
# 如果跟踪慢: 增大 MC_ROLL_P

# 测试方法: QGroundControl 中做阶跃输入
# 观察: 超调 < 20%, 调节时间 < 1s
```

---

## 5. 位置环调参

### 5.1 关键参数

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `MPC_XY_P` | 0.8 | 水平位置P |
| `MPC_XY_VEL_P_ACC` | 1.8 | 水平速度P |
| `MPC_XY_VEL_I_ACC` | 0.4 | 水平速度I |
| `MPC_XY_VEL_D_ACC` | 0.2 | 水平速度D |
| `MPC_Z_P` | 1.0 | 垂直位置P |
| `MPC_Z_VEL_P_ACC` | 4.0 | 垂直速度P |
| `MPC_Z_VEL_I_ACC` | 2.0 | 垂直速度I |
| `MPC_Z_VEL_D_ACC` | 0.0 | 垂直速度D |

### 5.2 位置环结构

```
位置误差 → MPC_XY_P → 期望速度
    ↓
速度误差 → MPC_XY_VEL_P_ACC → 期望加速度
    ↓
加速度 → 姿态控制器
```

### 5.3 调参方法

```bash
# 水平位置跟踪
param set MPC_XY_P 0.8     # 位置P (越大跟踪越快)
param set MPC_XY_VEL_P_ACC 1.8  # 速度P (响应刚度)
param set MPC_XY_VEL_D_ACC 0.2  # 速度D (阻尼)

# 垂直位置跟踪
param set MPC_Z_P 1.0      # 高度P
param set MPC_Z_VEL_P_ACC 4.0  # 垂直速度P

# 测试: QGroundControl 中拖动位置
# 观察: 跟踪误差、超调、振荡
```

---

## 6. 推力模型

### 6.1 推力-力矩关系

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `THR_MDL_FAC` | 0.0 | 推力模型系数 |
| `MPC_THR_HOVER` | 0.5 | 悬停油门 |
| `MPC_THR_MAX` | 1.0 | 最大油门 |
| `MPC_THR_MIN` | 0.12 | 最小油门 |

### 6.2 推力模型修正

```
实际推力 = 油门 × (1 - THR_MDL_FAC) + 油门² × THR_MDL_FAC
```

- `THR_MDL_FAC = 0`: 线性关系 (默认)
- `THR_MDL_FAC = 0.5`: 非线性修正 (更真实)
- `THR_MDL_FAC = 1.0`: 完全二次关系

```bash
# 设置推力模型
param set THR_MDL_FAC 0.3

# 调整悬停油门
param set MPC_THR_HOVER 0.5
```

---

## 7. 电调校准

### 7.1 为什么需要校准

- 不同电调的油门范围不一致
- 导致推力不均匀, 飞行不稳

### 7.2 校准方法

```bash
# 1. 取下螺旋桨!
# 2. 在 px4> 中:
commander disarm
pwm min
# 3. 接上电池
# 4. 等待校准完成
pwm max
# 5. 断开电池
pwm disarmed
```

---

## 8. 电池参数

### 8.1 关键参数

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `BAT_N_CELLS` | 0 | 电池节数 |
| `BAT_V_EMPTY` | 3.5 | 空载电压 |
| `BAT_V_FULL` | 4.2 | 满电电压 |
| `BAT_V_CHARGED` | 4.05 | 充电截止 |
| `BAT_LOW_THR` | 0.2 | 低压阈值 |
| `BAT_CRIT_THR` | 0.07 | 危险阈值 |

### 8.2 配置示例

```bash
# 4S LiPo 电池
param set BAT_N_CELLS 4
param set BAT_V_EMPTY 3.5
param set BAT_V_FULL 4.2
param set BAT_LOW_THR 0.2
param set BAT_CRIT_THR 0.07
```

---

## 9. 调参检查清单

### 9.1 起飞前检查

- [ ] 螺旋桨安装正确 (CW/CCW)
- [ ] 电机转向正确
- [ ] 电调已校准
- [ ] 遥控器通道映射正确
- [ ] 失控保护设置 (RTL/Land)
- [ ] 电池电压正常
- [ ] EKF2 收敛 (QGC 显示绿色)

### 9.2 调参后验证

- [ ] 悬停稳定 (无振荡)
- [ ] 阶跃响应 (超调 < 20%)
- [ ] 位置跟踪 (误差 < 0.3m)
- [ ] 抗风能力 (2m/s 风下稳定)
- [ ] 电池低压保护触发
- [ ] 遥控器丢失保护触发

---

## 10. 常见调参问题

### Q: 悬停时高频振荡

```bash
# 原因: 角速率环 P 或 D 太大
param set MC_ROLLRATE_P 0.1    # 减小
param set MC_ROLLRATE_D 0.002  # 减小
```

### Q: 转弯时掉高

```bash
# 原因: 垂直速度环 I 不够
param set MPC_Z_VEL_I_ACC 2.0  # 增大
```

### Q: 位置跟踪有稳态误差

```bash
# 原因: 速度环 I 不够
param set MPC_XY_VEL_I_ACC 0.4  # 增大
```

### Q: 松杆后飞机漂移

```bash
# 原因: 位置环增益太小
param set MPC_XY_P 1.0  # 增大
```

---

## 下一步

→ [04 — 源码阅读指南](04-code-reading.md)
