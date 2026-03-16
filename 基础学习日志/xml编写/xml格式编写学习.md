# MuJoCo 仿真建模：MJCF 文件架构与核心组件深度解析

在多体动力学仿真领域，**MJCF (MuJoCo XML)** 是一种基于 XML 格式的建模规范。其核心逻辑在于通过层次化的描述，定义机器人的运动学约束、物理属性以及执行器动力学。本文旨在梳理 MJCF 文件的关键元素及其配置准则。

---

## 1. 根元素与全局环境配置

每一个 MJCF 文件的顶层容器均为 `<mujoco>` 标签。在该节点下，通过特定的子标签定义仿真的基础环境与数值计算参数。

* **`<compiler>` 标签**：用于预处理模型选项。关键属性包括 `angle`（指定弧度 `radian` 或角度 `degree`）以及 `meshdir`（外部网格资源路径）。
* **`<option>` 标签**：配置物理引擎的核心参数。

```xml
<mujoco model="ur10e_robot">
    <compiler angle="radian" meshdir="assets" autolimits="true"/>
    
    <option gravity="0 0 -9.81" timestep="0.002"/>
</mujoco>