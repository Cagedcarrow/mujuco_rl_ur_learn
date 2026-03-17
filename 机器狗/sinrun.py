import mujoco
import mujoco.viewer
import numpy as np
import time

# 加载模型（包含 scene.xml 中定义的地面）
model = mujoco.MjModel.from_xml_path('scene.xml')
data = mujoco.MjData(model)

# 【核心步骤】将仿真状态强制重置到 XML 中定义的 "home" 关键帧
# 这会把机器人瞬间移动到空中并设置好蹲姿，而不是在地底下发生碰撞
if model.nkey > 0:
    mujoco.mj_resetDataKeyframe(model, data, 0)

print("仿真加载成功，正在启动可视化窗口...")

with mujoco.viewer.launch_passive(model, data) as viewer:
    # 模拟开始
    while viewer.is_running():
        step_start = time.time()

        # 物理步进
        # 注意：此时 data.ctrl 已经自动继承了 keyframe 中的值
        mujoco.mj_step(model, data)

        # 同步渲染
        viewer.sync()

        # 维持仿真速度与现实一致
        elapsed = time.time() - step_start
        if elapsed < model.opt.timestep:
            time.sleep(model.opt.timestep - elapsed)