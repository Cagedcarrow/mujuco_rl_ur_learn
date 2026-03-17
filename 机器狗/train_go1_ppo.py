import os
import time
import mujoco
import mujoco.viewer
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import torch

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecVideoRecorder, DummyVecEnv
from stable_baselines3.common.env_checker import check_env

# ================= 目录配置 =================
WORKSPACE_DIR = "./go1_ppo_results"
MODEL_DIR = os.path.join(WORKSPACE_DIR, "models")
LOG_DIR = os.path.join(WORKSPACE_DIR, "logs")
VIDEO_DIR = os.path.join(WORKSPACE_DIR, "videos")

# 创建所需的所有文件夹
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


class Go1Env(gym.Env):
    """为 Unitree Go1 编写的 Gymnasium 环境（支持离屏渲染和视频录制）"""
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 50}

    def __init__(self, xml_path='scene.xml', render_mode=None):
        super().__init__()
        self.model = mujoco.MjModel.from_xml_path(xml_path)
        self.data = mujoco.MjData(self.model)
        self.render_mode = render_mode
        self.viewer = None
        self.renderer = None # 用于离屏渲染（录视频）

        self.frame_skip = 20
        self.dt = self.model.opt.timestep * self.frame_skip

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(12,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(35,), dtype=np.float32)

        self.nom_pos = np.array([0, 0.8, -1.5,  0, 0.8, -1.5,  0, 0.8, -1.5,  0, 0.8, -1.5])
        self.action_scale = 0.5 

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        
        if self.model.nkey > 0:
            mujoco.mj_resetDataKeyframe(self.model, self.data, 0)
        
        # 随机初始化噪声
        noise = self.np_random.uniform(low=-0.05, high=0.05, size=self.model.nq)
        self.data.qpos[:] += noise
        mujoco.mj_forward(self.model, self.data)

        return self._get_obs(), {}

    def _get_obs(self):
        qpos = self.data.qpos[2:].copy()
        qvel = self.data.qvel.copy()
        return np.concatenate([qpos, qvel]).astype(np.float32)

    def step(self, action):
        target_pos = self.nom_pos + action * self.action_scale
        x_before = self.data.qpos[0]

        self.data.ctrl[:] = target_pos
        for _ in range(self.frame_skip):
            mujoco.mj_step(self.model, self.data)

        x_after = self.data.qpos[0]
        velocity_x = (x_after - x_before) / self.dt
        
        # 奖励函数
        forward_reward = velocity_x * 2.0
        healthy_reward = 1.0
        ctrl_cost = 0.05 * np.sum(np.square(action))
        reward = forward_reward + healthy_reward - ctrl_cost

        # 终止条件：跌倒或飞天
        z_height = self.data.qpos[2]
        terminated = bool(z_height < 0.18 or z_height > 0.5)
        truncated = False

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        if self.render_mode == "human":
            if self.viewer is None:
                self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
            self.viewer.sync()
            time.sleep(self.dt)
            
        elif self.render_mode == "rgb_array":
            # 录制视频需要的离屏渲染器 (分辨率 640x480)
            if self.renderer is None:
                self.renderer = mujoco.Renderer(self.model, 480, 640)
            self.renderer.update_scene(self.data)
            return self.renderer.render()

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
        if self.renderer is not None:
            self.renderer.close()


# 用于创建多进程环境的辅助函数
def make_env(xml_path, rank, seed=0):
    def _init():
        env = Go1Env(xml_path=xml_path, render_mode=None)
        env.reset(seed=seed + rank)
        return env
    return _init


if __name__ == "__main__":
    # 确认你的 GPU 可用
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"============== 开始训练 ==============")
    print(f"正在使用的计算设备: {device.upper()}")
    print(f"工作区目录: {WORKSPACE_DIR}")

    # 1. 启动多进程并行环境 (压榨 CPU 和 GPU)
    num_envs = 8  # 开启 8 个并行环境（如果你的 CPU 有 16 核以上，可以调高到 16）
    xml_file = 'scene.xml'
    
    # 使用 SubprocVecEnv 开启多进程
    train_env = SubprocVecEnv([make_env(xml_file, i) for i in range(num_envs)])

    # 2. 初始化 PPO 模型
    # 针对 GPU 加速优化：增大了 batch_size 和 n_steps
    model = PPO(
        "MlpPolicy", 
        train_env, 
        verbose=1, 
        n_steps=2048,           # 每个环境收集的步数
        batch_size=512,         # GPU 训练的批次大小，RTX4060 设为 512 毫不费力
        tensorboard_log=LOG_DIR,
        device=device
    )

    # 3. 开始训练
    # 设定训练步数，300万步(3M)在 8 环境 + RTX 4060 下大概需要 15~30 分钟
    total_timesteps = 3000000 
    print(f"开始执行 {total_timesteps} 步的训练...")
    
    model.learn(total_timesteps=total_timesteps)

    # 4. 保存模型
    model_path = os.path.join(MODEL_DIR, "ppo_go1_final")
    model.save(model_path)
    print(f"模型已成功保存至: {model_path}.zip")
    train_env.close()

    # =================================================================
    # 5. 测试与录制视频
    # =================================================================
    print("============== 训练完成，开始录制测试视频 ==============")
    
    # 重新创建一个用于录制视频的单环境 (注意 render_mode="rgb_array")
    # 我们用 DummyVecEnv 包装它以兼容 VecVideoRecorder
    test_env = DummyVecEnv([lambda: Go1Env(xml_path=xml_file, render_mode="rgb_array")])
    
    # 配置视频录制器
    # 录制长度设定为 1000 步（约 20 秒）
    video_length = 1000
    test_env = VecVideoRecorder(
        test_env, 
        VIDEO_DIR,
        record_video_trigger=lambda x: x == 0, # 从第 0 步开始录制
        video_length=video_length,
        name_prefix="go1_trained"
    )

    # 加载刚训练好的模型
    eval_model = PPO.load(model_path)
    obs = test_env.reset()
    
    print("正在生成视频帧，请稍候...")
    for _ in range(video_length + 1):
        action, _states = eval_model.predict(obs, deterministic=True)
        obs, reward, done, info = test_env.step(action)
        # VecVideoRecorder 会自动捕捉 render("rgb_array") 的画面
    
    test_env.close()
    print(f"视频录制完成！请在文件夹中查看: {VIDEO_DIR}")