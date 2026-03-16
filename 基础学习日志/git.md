# Git 常用命令速查表

## 📋 目录
- [基础配置](#基础配置)
- [日常操作](#日常操作)
- [历史与撤销](#历史与撤销)
- [分支管理](#分支管理)
- [远程协作](#远程协作)
- [标签管理](#标签管理)
- [实用技巧](#实用技巧)
- [工作流程](#工作流程)

## 🔧 基础配置

| 命令 | 说明 | 示例 |
|------|------|------|
| `git init` | 初始化新仓库 | `git init` |
| `git clone [url]` | 克隆远程仓库 | `git clone https://github.com/user/repo.git` |
| `git config --global user.name "[name]"` | 设置全局用户名 | `git config --global user.name "张三"` |
| `git config --global user.email "[email]"` | 设置全局邮箱 | `git config --global user.email "zhangsan@example.com"` |
| `git config --list` | 查看所有配置 | `git config --list` |

## 📝 日常操作

| 命令 | 说明 | 示例 |
|------|------|------|
| `git status` | 查看工作区状态 | `git status` |
| `git add [file]` | 添加文件到暂存区 | `git add index.html` |
| `git add .` | 添加所有修改 | `git add .` |
| `git commit -m "[msg]"` | 提交更改 | `git commit -m "修复登录bug"` |
| `git commit -am "[msg]"` | 添加并提交（跳过暂存） | `git commit -am "快速提交"` |
| `git diff` | 查看未暂存的修改 | `git diff` |
| `git diff --staged` | 查看已暂存的修改 | `git diff --staged` |

## ⏪ 历史与撤销

| 命令 | 说明 | 注意 |
|------|------|------|
| `git log` | 查看提交历史 | `git log --oneline`（简洁模式） |
| `git log --graph` | 图形化查看分支历史 | `git log --graph --oneline` |
| `git checkout [file]` | 丢弃工作区修改 | `git checkout index.html` |
| `git restore [file]` | 恢复文件（Git 2.23+） | `git restore index.html` |
| `git reset [file]` | 从暂存区移除文件 | `git reset index.html` |
| `git reset --soft [commit]` | 重置到指定提交，保留修改 | 安全 |
| `git reset --hard [commit]` | 重置到指定提交，丢弃修改 | **危险！会丢失未提交的修改** |
| `git revert [commit]` | 创建新提交来撤销指定提交 | 安全，推荐用于已推送的提交 |

## 🌿 分支管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `git branch` | 查看本地分支 | `git branch -v`（查看详情） |
| `git branch [name]` | 创建新分支 | `git branch feature-login` |
| `git checkout [name]` | 切换到分支 | `git checkout feature-login` |
| `git checkout -b [name]` | 创建并切换分支 | `git checkout -b feature-login` |
| `git switch [name]` | 切换分支（Git 2.23+） | `git switch feature-login` |
| `git switch -c [name]` | 创建并切换（Git 2.23+） | `git switch -c feature-login` |
| `git merge [name]` | 合并分支到当前分支 | `git merge feature-login` |
| `git branch -d [name]` | 删除已合并的分支 | `git branch -d feature-login` |
| `git branch -D [name]` | 强制删除分支 | `git branch -D temp-branch` |

## 🌐 远程协作

| 命令 | 说明 | 示例 |
|------|------|------|
| `git remote -v` | 查看远程仓库 | `git remote -v` |
| `git remote add [name] [url]` | 添加远程仓库 | `git remote add origin https://github.com/user/repo.git` |
| `git fetch [remote]` | 获取远程更新（不合并） | `git fetch origin` |
| `git pull` | 拉取并合并远程更新 | `git pull origin main` |
| `git push` | 推送本地提交 | `git push origin main` |
| `git push -u origin [branch]` | 推送并设置上游分支 | `git push -u origin feature-login` |
| `git push --force` | 强制推送（覆盖远程） | **谨慎使用！会覆盖他人提交** |

## 🏷️ 标签管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `git tag` | 查看所有标签 | `git tag` |
| `git tag [name]` | 创建轻量标签 | `git tag v1.0.0` |
| `git tag -a [name] -m "[msg]"` | 创建带注释的标签 | `git tag -a v1.0.0 -m "正式版发布"` |
| `git push origin [tag]` | 推送标签到远程 | `git push origin v1.0.0` |
| `git push origin --tags` | 推送所有标签 | `git push origin --tags` |

## 💡 实用技巧

### 1. 查看简洁日志
```bash
git log --oneline --graph --all
```

### 2. 查看某人的提交
```bash
git log --author="张三"
```

### 3. 搜索提交信息
```bash
git log --grep="bug"
```

### 4. 查看文件修改历史
```bash
git log -p index.html
```

### 5. 暂存当前修改（临时保存）
```bash
git stash          # 暂存修改
git stash list     # 查看暂存列表
git stash pop      # 恢复最近暂存的修改
```

## 🔄 推荐工作流程

### 日常开发流程
```bash
# 1. 开始新功能
git checkout main
git pull origin main
git checkout -b feature-new

# 2. 开发并提交
git add .
git commit -m "添加新功能"

# 3. 推送到远程
git push -u origin feature-new

# 4. 创建 Pull Request（在 GitHub/GitLab 上）

# 5. 合并后清理
git checkout main
git pull origin main
git branch -d feature-new
```

### 解决冲突流程
```bash
# 1. 拉取最新代码（可能会产生冲突）
git pull origin main

# 2. 查看冲突文件
git status

# 3. 手动解决冲突（编辑文件）

# 4. 标记冲突已解决
git add [冲突文件]

# 5. 完成合并
git commit -m "解决合并冲突"