#!/usr/bin/env python3
"""
MiniMax Token 检查工具
检查 API Token 剩余配额，支持定时监控和 Telegram 通知

用法:
    python3 minimax_token.py --check     # 单次检查
    python3 minimax_token.py --monitor   # 定时监控
"""
import os
import sys
import time
import json
import requests
import logging
import argparse
from datetime import datetime

# 配置日志 - 使用环境变量，可自定义日志路径
LOG_DIR = os.environ.get('OPENCLAW_LOG_DIR', os.path.expanduser('~/.openclaw/logs'))
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, 'token_monitor.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============ 配置项 (请修改以下值) ============
# 优先从环境变量读取，也可以在运行时传入
TOKEN_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
# TODO: 替换为你的 Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
# TODO: 替换为你的 Telegram Chat ID
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
# 检查间隔 (秒), 默认 1 小时
CHECK_INTERVAL = 3600


def get_token_remaining():
    """查询 MiniMax API 剩余配额"""
    import subprocess
    
    # 从环境变量或配置文件读取 API Key
    api_key = os.environ.get('MINIMAX_API_KEY', TOKEN_API_KEY)
    if not api_key or api_key == 'YOUR_API_KEY':
        return {"error": "请设置 MINIMAX_API_KEY 环境变量"}
    
    cmd = [
        "curl", "-s", "--location",
        "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains",
        "--header", f"Authorization: Bearer {api_key}",
        "--header", "Content-Type: application/json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.error(f"curl failed: {result.stderr}")
            return {"error": result.stderr}
        
        data = json.loads(result.stdout)
        logger.info(f"API Response: {data}")
        return data
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return {"error": str(e)}


def format_token_message(data):
    """格式化 Token 信息为可读消息"""
    if "error" in data:
        return f"❌ Token 查询失败: {data['error']}"
    
    try:
        model_remains = data.get("model_remains", [])
        if not model_remains:
            return f"❌ 无法解析 Token 数据"
        
        m = model_remains[0]
        model_name = m.get("model_name", "Unknown")
        remains_time_sec = m.get("remains_time", 0) / 1000
        total = m.get("current_interval_total_count", 0)
        remaining = m.get("current_interval_usage_count", 0)
        used = total - remaining
        
        hours = int(remains_time_sec // 3600)
        minutes = int((remains_time_sec % 3600) // 60)
        
        return f"📊 *{model_name}* 配额状态\n\n• 剩余时间: {hours}小时 {minutes}分钟\n• 本周期: 已用 {used}/{total} 次\n• 剩余: {remaining} 次"
        
    except Exception as e:
        logger.error(f"Failed to parse token data: {e}")
        return f"📊 Token 状态\n\n原始响应:\n{json.dumps(data, indent=2)}"


def send_telegram_message(message):
    """通过 Telegram Bot 发送消息"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN)
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    
    if not bot_token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未配置, 跳过通知")
        print(f"[TOKEN] {message}")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        logger.info("Telegram 消息发送成功")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram 通知失败: {e}")
        return False


def check_once():
    """单次检查"""
    logger.info("执行 Token 配额检查...")
    data = get_token_remaining()
    message = format_token_message(data)
    print(message)
    send_telegram_message(message)
    return data


def monitor():
    """定时监控模式"""
    logger.info("Token 监控已启动")
    
    # 首次检查
    check_once()
    
    # 循环检查
    while True:
        time.sleep(CHECK_INTERVAL)
        data = get_token_remaining()
        timestamp = datetime.now().strftime("%H:%M")
        message = f"⏰ [{timestamp}] {format_token_message(data)}"
        print(message)
        send_telegram_message(message)


def main():
    parser = argparse.ArgumentParser(description="MiniMax Token 检查工具")
    parser.add_argument("--check", action="store_true", help="单次检查 Token 余额")
    parser.add_argument("--monitor", action="store_true", help="启动定时监控")
    parser.add_argument("--api-key", help="MiniMax API Key (或设置 MINIMAX_API_KEY 环境变量)")
    
    args = parser.parse_args()
    
    # 如果传入 API Key，临时使用
    if args.api_key:
        os.environ['MINIMAX_API_KEY'] = args.api_key
    
    if args.check:
        check_once()
    elif args.monitor:
        monitor()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
