---
name: minimax-token
description: 检查 MiniMax API Token 剩余配额。支持定时检查并通过 Telegram 发送通知。适用于：查询 Token 余额、配置定时监控、设置余额不足提醒。
---

# MiniMax Token 检查工具

查询 MiniMax API 的 Token 剩余配额，支持定时检查和 Telegram 通知。

## 配置

首次使用前需要配置以下参数：

```python
# 在脚本中修改以下配置
TOKEN_API_KEY = "sk-cp-xxxxxxxxxx"  # 你的 MiniMax API Key
TELEGRAM_BOT_TOKEN = "your_bot_token"  # 你的 Telegram Bot Token
TELEGRAM_CHAT_ID = "your_chat_id"  # 你的 Telegram Chat ID
```

## 使用方法

### 1. 手动检查 Token 余额

```bash
python3 /path/to/minimax_token.py --check
```

### 2. 启动定时监控（每小时检查一次）

```bash
python3 /path/to/minimax_token.py --monitor
```

### 3. 作为系统服务运行（Linux）

```bash
# 安装服务
sudo cp minimax-token.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable minimax-token
sudo systemctl start minimax-token

# 查看日志
journalctl -u minimax-token -f
```

## 依赖

```bash
pip3 install requests
```

## 定时任务

可以通过 OpenClaw cron 配置定时检查：

```
每小时检查一次：schedule: every 1 hour
```

## 输出示例

```
📊 MiniMax-M2.5 配额状态

• 剩余时间: 50小时 30分钟
• 本周期: 已用 150/1000 次
• 剩余: 850 次
```
