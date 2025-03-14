import json
import asyncio
from typing import Optional, Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from constants import *
from create_messages import *
from amazon_api import AmazonAPI
import httpx
import os

app = FastAPI(title="Amazon Telegram Bot")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 环境变量配置
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', TELEGRAM_TOKEN)
CHANNEL_ID = int(os.getenv('CHANNEL_ID', CHANNEL_ID))

async def send_telegram_request(method: str, params: dict) -> dict:
    """异步发送Telegram API请求"""
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(base_url, data=params)
            return response.json()
        except Exception as e:
            print(f"API请求失败 ({method}): {e}")
            return {"ok": False}

async def send_telegram_message(chat_id: Union[int, str], text: str) -> bool:
    """异步发送消息到Telegram"""
    result = await send_telegram_request('sendMessage', {
        'chat_id': str(chat_id),
        'text': text,
        'parse_mode': 'HTML'
    })
    return result.get('ok', False)

async def send_telegram_photo(chat_id: Union[int, str], photo_url: str, caption: str) -> bool:
    """异步发送图片到Telegram"""
    result = await send_telegram_request('sendPhoto', {
        'chat_id': str(chat_id),
        'photo': photo_url,
        'caption': caption,
        'parse_mode': 'HTML'
    })
    return result.get('ok', False)

async def handle_amazon_link(message_text: str):
    """异步处理Amazon链接"""
    try:
        print(f"处理链接: {message_text}")
        amazon_api = AmazonAPI()
        product = amazon_api.get_product_from_url(message_text)

        if not product:
            print("无法获取产品信息")
            return

        formatted_message = create_product_post(product)
        if formatted_message == "Sorry, couldn't retrieve product information.":
            print("无法创建产品信息")
            return

        # 尝试发送图片
        if (hasattr(product, 'images') and
            hasattr(product.images, 'primary') and
            hasattr(product.images.primary, 'large') and
            product.images.primary.large and
            product.images.primary.large.url):

            image_url = product.images.primary.large.url.replace('_SL500_', '_SL1500_')
            print(f"尝试发送图片: {image_url}")

            if await send_telegram_photo(CHANNEL_ID, image_url, formatted_message):
                return

        print("发送纯文本消息")
        await send_telegram_message(CHANNEL_ID, formatted_message)

    except Exception as e:
        print(f"处理Amazon链接时出错: {e}")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """处理来自Telegram的webhook请求"""
    try:
        update = await request.json()
        message = update.get("message", {})

        if not message:
            return {"ok": True}

        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if not text:
            return {"ok": True}

        if text == "/start":
            name = message.get("from", {}).get("first_name", "")
            welcome_message = (f"Benvenuto {name}, mandami il link amazon di un prodotto per "
                           "creare il post sul tuo canale!")
            await send_telegram_message(chat_id, welcome_message)
        elif "amazon." in text and ("/dp/" in text or "/gp/product/" in text):
            await handle_amazon_link(text)

        return {"ok": True}
    except Exception as e:
        print(f"处理webhook请求时出错: {e}")
        return {"ok": False, "error": str(e)}

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "Bot is running",
        "telegram_token": TELEGRAM_TOKEN[:10] + "...",
        "channel_id": CHANNEL_ID
    }

# 为Vercel部署添加必要的变量
app.state.telegram_token = TELEGRAM_TOKEN
app.state.channel_id = CHANNEL_ID

# 导出 app 变量给 Vercel
app = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
