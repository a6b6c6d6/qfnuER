import time
import hmac
import hashlib
import base64
import requests
import logging
import urllib.parse
import json
import os
from datetime import datetime

####感谢qwen的伟大付出（我就写了一点点
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def dingtalk(title: str, content: str) -> dict:
    # 从环境变量获取配置
    DINGTALK_BOT_WEBHOOK = os.getenv("DINGTALK_BOT_WEBHOOK")
    DINGTALK_BOT_SECRET = os.getenv("DINGTALK_BOT_SECRET")
   
    # 检查必要配置
    if not DINGTALK_BOT_WEBHOOK or not DINGTALK_BOT_SECRET:
        logging.error("钉钉Webhook或密钥未配置")
        return {"error": "钉钉Webhook或密钥未配置"}


    # 计算签名
    timestamp = str(round(time.time() * 1000))
    secret_enc = DINGTALK_BOT_SECRET.encode("utf-8")
    string_to_sign = f"{timestamp}\n{DINGTALK_BOT_SECRET}"
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode("utf-8"))


    # 构建完整Webhook地址
    webhook_url = f"{DINGTALK_BOT_WEBHOOK}&timestamp={timestamp}&sign={sign}"


    # 构建请求头
    headers = {"Content-Type": "application/json"}


    # 构建消息内容
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"#### {title}\n{content}"
        }
    }


    # 发送请求
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(msg))
        logging.info(f"钉钉发送通知消息成功\n{response.json()}")
        return response.json()
    except Exception as e:
        logging.error(f"钉钉发送通知消息失败\n{e}")
        return {"error": str(e)}


def pa():
    # 从环境变量获取URL
    WECHAT_API_URL = os.getenv("WECHAT_API_URL")
   
    if not WECHAT_API_URL:
        logging.error("微信API URL未配置")
        return
   
    # 从环境变量获取阈值，如果未配置则使用默认值
    threshold_str = os.getenv("BALANCE_THRESHOLD", "46.1234")
    try:
        c = float(threshold_str)
    except ValueError:
        logging.warning(f"阈值配置错误，使用默认值 46.1234")
        c = 46.1234
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0'
    }
   
    try:
        response = requests.get(WECHAT_API_URL, headers=headers)
        aaa = response.text
        num_str = ''.join(aaa[i] for i in range(75, 82))
        b = float(num_str)
        b_5 = round(b, 5)
        logging.info(f"获取到余额: {b_5} 元, 阈值: {c} 元")
           
        if c > b:
            result = dingtalk("余额提醒", f"您的余额为{b_5}元,请及时充值\n当前余额阈值为{c}元")
            logging.info(f"发送提醒结果: {result}")
        else:
            logging.info("余额充足")

           
    except Exception as e:
        logging.error(f"获取余额失败: {e}")


if __name__ == "__main__":
    pa()