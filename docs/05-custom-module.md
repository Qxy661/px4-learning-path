# 05 — 自定义模块开发

> 目标: 学会编写、编译、运行自定义PX4模块

---

## 1. 模块基础

### 1.1 PX4 模块结构

每个模块是独立的可执行程序, 通过 uORB 通信:

```
my_module/
├── CMakeLists.txt        # 编译配置
├── MyModule.cpp          # 主文件
├── MyModule.hpp          # 头文件
└── Kconfig               # 配置菜单
```

### 1.2 模块生命周期

```cpp
#include <px4_platform_common/module.h>

class MyModule : public ModuleBase<MyModule>, public ModuleParams
{
public:
    MyModule(int example_param, bool example_flag);
    ~MyModule() override;

    static int task_spawn(int argc, char *argv[]);
    static MyModule *instantiate(int argc, char *argv[]);
    static int custom_command(int argc, char *argv[]);
    static int print_usage(const char *reason = nullptr);

    void run() override;
};
```

---

## 2. Hello Sky 示例

### 2.1 创建模块

```bash
# 进入 PX4 目录
cd ~/PX4-Autopilot

# 创建模块目录
mkdir src/examples/hello_sky
```

### 2.2 编写代码

**src/examples/hello_sky/HelloSky.cpp**:

```cpp
#include <px4_platform_common/module.h>
#include <px4_platform_common/log.h>

class HelloSky : public ModuleBase<HelloSky>
{
public:
    HelloSky() = default;
    ~HelloSky() override = default;

    static int task_spawn(int argc, char *argv[])
    {
        // 创建任务
        _task_id = px4_task_spawn_cmd(
            "hello_sky",
            SCHED_DEFAULT,
            SCHED_PRIORITY_DEFAULT,
            1024,
            (px4_main_t)&run_trampoline,
            (char *const *)argv
        );

        if (_task_id < 0) {
            _task_id = -1;
            return -errno;
        }

        return 0;
    }

    static int custom_command(int argc, char *argv[])
    {
        return print_usage("unknown command");
    }

    static int print_usage(const char *reason = nullptr)
    {
        if (reason) {
            PX4_WARN("%s\n", reason);
        }

        PRINT_MODULE_DESCRIPTION(
            R"STR(
## Description
Hello Sky example module.

## Example
$ hello_sky start
$ hello_sky stop
)STR"
        );

        PRINT_MODULE_USAGE_NAME("hello_sky", "example");
        PRINT_MODULE_USAGE_COMMAND("start");
        PRINT_MODULE_USAGE_COMMAND("stop");

        return 0;
    }

    static int run_trampoline(int argc, char *argv[])
    {
        HelloSky *instance = instantiate(argc, argv);

        if (instance) {
            _object.store(instance);
            instance->run();
            delete instance;
            _object.store(nullptr);
        }

        return 0;
    }

    void run() override
    {
        PX4_INFO("Hello Sky! 模块已启动");

        // 主循环
        while (!should_exit()) {
            PX4_INFO("Hello Sky! 运行中...");
            px4_usleep(1000000);  // 1秒
        }

        PX4_INFO("Hello Sky! 模块已停止");
    }

private:
    static px4_task_t _task_id;
    static atomic<HelloSky *> _object;
};

px4_task_t HelloSky::_task_id = -1;
atomic<HelloSky *> HelloSky::_object{nullptr};

extern "C" __EXPORT int hello_sky_main(int argc, char *argv[])
{
    return HelloSky::main(argc, argv);
}
```

### 2.3 CMakeLists.txt

```cmake
px4_add_module(
    MODULE examples__hello_sky
    MAIN hello_sky
    SRCS
        HelloSky.cpp
    DEPENDS
        px4_platform
)
```

### 2.4 编译和运行

```bash
# 编译
make px4_sitl_default

# 启动 SITL
make px4_sitl gz_x500

# 在 px4> 中运行模块
hello_sky start

# 停止模块
hello_sky stop
```

---

## 3. uORB 订阅示例

### 3.1 订阅传感器数据

```cpp
#include <px4_platform_common/module.h>
#include <uORB/topics/sensor_accel.h>
#include <uORB/Subscription.hpp>

class SensorListener : public ModuleBase<SensorListener>
{
public:
    void run() override
    {
        // 订阅加速度计
        uORB::Subscription sensor_accel_sub{ORB_ID(sensor_accel)};

        while (!should_exit()) {
            sensor_accel_s accel{};

            if (sensor_accel_sub.update(&accel)) {
                PX4_INFO("Accel: x=%.2f, y=%.2f, z=%.2f [m/s²]",
                    (double)accel.x, (double)accel.y, (double)accel.z);
            }

            px4_usleep(100000);  // 100ms
        }
    }
};
```

### 3.2 发布 uORB 消息

```cpp
#include <uORB/Publication.hpp>
#include <uORB/topics/vehicle_command.h>

void publish_command()
{
    uORB::Publication<vehicle_command_s> cmd_pub{ORB_ID(vehicle_command)};
    
    vehicle_command_s cmd{};
    cmd.timestamp = hrt_absolute_time();
    cmd.command = vehicle_command_s::VEHICLE_CMD_DO_SET_MODE;
    cmd.param1 = 1;  // custom mode
    cmd.target_system = 1;
    cmd.target_component = 1;
    
    cmd_pub.publish(cmd);
}
```

---

## 4. 参数定义

### 4.1 添加自定义参数

**src/examples/my_module/params.c**:

```c
#include <px4_platform_common/px4_config.h>
#include <parameters/param.h>

PARAM_DEFINE_INT32(MY_PARAM1, 42);
PARAM_DEFINE_FLOAT(MY_PARAM2, 3.14f);
```

### 4.2 在代码中使用参数

```cpp
#include <px4_platform_common/module_params.h>

class MyModule : public ModuleBase<MyModule>, public ModuleParams
{
public:
    MyModule() : ModuleParams(nullptr)
    {
        // 参数会自动更新
    }

    void run() override
    {
        while (!should_exit()) {
            // 读取参数
            int32_t param1 = _param_my_param1.get();
            float param2 = _param_my_param2.get();
            
            PX4_INFO("Param1=%d, Param2=%.2f", param1, (double)param2);
            px4_usleep(1000000);
        }
    }

private:
    // 定义参数句柄
    DEFINE_PARAMETERS(
        (ParamInt<px4::params::MY_PARAM1>) _param_my_param1,
        (ParamFloat<px4::params::MY_PARAM2>) _param_my_param2
    )
};
```

---

## 5. 工作队列示例

### 5.1 使用工作队列

```cpp
#include <px4_platform_common/px4_workqueue.h>

class MyWorkItem : public ModuleBase<MyWorkItem>
{
public:
    void run() override
    {
        // 初始化工作
        _work = {};
        
        // 调度工作
        work_queue(HPWORK, &_work, (worker_t)&MyWorkItem::cycle_trampoline, this, 0);
        
        while (!should_exit()) {
            px4_usleep(1000);
        }
        
        // 取消工作
        work_cancel(HPWORK, &_work);
    }

private:
    work_s _work{};
    
    static void cycle_trampoline(void *arg)
    {
        MyWorkItem *instance = static_cast<MyWorkItem *>(arg);
        instance->cycle();
    }
    
    void cycle()
    {
        // 周期性工作
        PX4_INFO("Cycle running...");
        
        // 重新调度
        work_queue(HPWORK, &_work, (worker_t)&MyWorkItem::cycle_trampoline, this, USEC2TICK(1000000));
    }
};
```

---

## 6. Mavlink 模块示例

### 6.1 发送自定义 MAVLink 消息

```cpp
#include <mavlink.h>
#include <uORB/topics/vehicle_command.h>

void send_custom_mavlink()
{
    mavlink_message_t msg;
    mavlink_msg_named_value_float_pack(
        1,  // system_id
        1,  // component_id
        &msg,
        hrt_absolute_time() / 1000,
        "my_value",
        42.0f
    );
    
    // 发送到 MAVLink 通道
    mavlink_mission_item_t *mission_item = ...;
}
```

---

## 7. 调试模块

### 7.1 添加日志

```cpp
#include <px4_platform_common/log.h>

PX4_INFO("信息: %d", value);     // 普通信息
PX4_WARN("警告: %s", "msg");     // 警告
PX4_ERR("错误: %.2f", val);      // 错误
PX4_DEBUG("调试: %d", debug);    // 调试 (仅debug模式)
```

### 7.2 使用 MAVLink 控制台

```bash
# 在 px4> 中查看日志
dmesg

# 查看模块状态
my_module status
```

### 7.3 使用 gdb 调试

```bash
# 在 SITL 中调试特定模块
gdb --args ./build/px4_sitl_default/bin/px4 -s etc/init.d-posix/rcS

# 设置断点
b MyModule::run

# 运行
run
```

---

## 8. 实验练习

### 练习 1: Hello Sky

```bash
# 1. 创建 hello_sky 模块
# 2. 编译并运行
# 3. 观察输出
```

### 练习 2: 传感器监听

```bash
# 1. 创建监听 vehicle_attitude 的模块
# 2. 输出姿态四元数
# 3. 与 listener vehicle_attitude 对比
```

### 练习 3: 自定义参数

```bash
# 1. 添加自定义参数
# 2. 在 QGroundControl 中修改
# 3. 在模块中读取并显示
```

---

## 下一步

→ [06 — ROS2 集成](06-ros2-integration.md)
