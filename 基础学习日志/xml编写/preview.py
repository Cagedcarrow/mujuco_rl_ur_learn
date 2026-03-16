import mujoco
import mujoco.viewer
import time

# 1. 加载模型文件
# 如果你的 XML 文件和 Python 脚本在同一个文件夹，直接写文件名
# 否则请填写完整路径
model_path = "pogo_bot.xml" 
model = mujoco.MjModel.from_xml_path(model_path)
data = mujoco.MjData(model)

# 2. 启动交互式查看器
# launch_passive 会启动一个允许你在后台继续执行代码的窗口
with mujoco.viewer.launch_passive(model, data) as viewer:
    # 保持窗口开启
    while viewer.is_running():
        step_start = time.time()

        # 物理仿真步进
        mujoco.mj_step(model, data)

        # 刷新查看器（这里可以同步你的修改）
        viewer.sync()

        # 控制仿真速度，使其接近真实时间
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)