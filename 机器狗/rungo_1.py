import mujoco
import mujoco.viewer
import numpy as np
import time

# 加载模型
model = mujoco.MjModel.from_xml_path('scene.xml')
data = mujoco.MjData(model)

# 重置到稳定的站立姿态 (关键步骤)
if model.nkey > 0:
    mujoco.mj_resetDataKeyframe(model, data, 0)

print("开始执行 Trot(对角) 步态...")

# ================= 步态参数调节区 =================
freq = 2.0          # 步频 (Hz)：每秒迈多少步，越大走得越快
stride_amp = 0.3    # 步幅大小：髋关节前后摆动的幅度 (弧度)
swing_amp = 0.5     # 抬腿高度：小腿关节弯曲的幅度 (弧度)

# 标称站立姿态 (与 xml 中的 keyframe 保持一致)
nom_abduct = 0.0    # 侧摆关节 (保持0，不往两边撇)
nom_hip = 0.8       # 髋关节基准角度
nom_calf = -1.5     # 小腿关节基准角度
# ==================================================

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        step_start = time.time()
        t = data.time
        
        # 1. 计算两组腿的相位 (Phase)
        # phase1 和 phase2 永远相差 pi (180度)
        phase1 = 2 * np.pi * freq * t
        phase2 = phase1 + np.pi
        
        # 2. 计算 Group 1 (FR, RL) 的目标角度
        # 髋关节：正弦波前后摆动
        hip1 = nom_hip + stride_amp * np.sin(phase1)
        # 小腿关节：当 cos(phase) > 0 时抬起腿 (数值变小即弯曲)，否则保持伸直踩地
        calf1 = nom_calf - swing_amp * np.maximum(0, np.cos(phase1))
        
        # 3. 计算 Group 2 (FL, RR) 的目标角度
        hip2 = nom_hip + stride_amp * np.sin(phase2)
        calf2 = nom_calf - swing_amp * np.maximum(0, np.cos(phase2))
        
        # 4. 组装 12 个电机的控制指令
        # 顺序: FR(abd, hip, calf), FL(...), RR(...), RL(...)
        target_pos = np.array([
            nom_abduct, hip1, calf1,  # FR 右前腿 (Group 1)
            nom_abduct, hip2, calf2,  # FL 左前腿 (Group 2)
            nom_abduct, hip2, calf2,  # RR 右后腿 (Group 2)
            nom_abduct, hip1, calf1   # RL 左后腿 (Group 1)
        ])
        
        # 5. 发送指令并进行物理仿真
        data.ctrl[:] = target_pos
        mujoco.mj_step(model, data)
        viewer.sync()
        
        # 6. 控制仿真速度与真实时间同步
        elapsed = time.time() - step_start
        if elapsed < model.opt.timestep:
            time.sleep(model.opt.timestep - elapsed)