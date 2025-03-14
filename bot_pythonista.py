import json
import time
import sys
import urllib.request
import urllib.parse
import traceback
from constants import *
from create_messages import *
from amazon_api import AmazonAPI
from keep_alive import start_keep_alive

MAX_RETRIES = 3
RETRY_DELAY = 5
def send_telegram_request(method, params):
    """发送Telegram API请求"""
    for _ in range(3):  # 尝试3次
        try:
            # 构建URL
            base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"

            # 调试信息
            print(f"发送请求到 {method}:")
            print(f"参数: {params}")

            # 构建请求头
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
            }

            # 编码参数
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote).encode('utf-8')

            # 创建请求
            req = urllib.request.Request(
                base_url,
                data=encoded_params,
                headers=headers,
                method='POST'
            )

            # 发送请求
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                print(f"API响应: {data}")
                return data

        except Exception as e:
            print(f"API请求失败 ({method}): {e}")
            print(traceback.format_exc())
            time.sleep(1)
    return {"ok": False}

def send_telegram_message(chat_id, text):
    """发送消息到Telegram"""
    result = send_telegram_request('sendMessage', {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    })
    return result.get('ok', False)

def send_telegram_photo(chat_id, photo_url, caption):
    """发送图片到Telegram"""
    result = send_telegram_request('sendPhoto', {
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption,
        'parse_mode': 'HTML'
    })
    return result.get('ok', False)

def handle_amazon_link(message_text):
    """处理Amazon链接"""
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

            if send_telegram_photo(CHANNEL_ID, image_url, formatted_message):
                return

        print("发送纯文本消息")
        send_telegram_message(CHANNEL_ID, formatted_message)

    except Exception as e:
        print(f"处理Amazon链接时出错: {e}")
        print(traceback.format_exc())

def main():
    """主函数"""
    # 配置SSL
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    print("启动机器人...")
    last_update_id = 0

    while True:
        try:

            updates = []

            try:
                data = send_telegram_request('getUpdates', {
                    'offset': last_update_id,
                    'timeout': 30
                })

                if not isinstance(data, dict):
                    print(f"获取更新返回了意外的数据类型: {type(data)}")
                    time.sleep(5)
                    continue

                if not data.get('ok'):
                    print(f"API返回错误: {data.get('description', 'Unknown error')}")
                    time.sleep(5)
                    continue

                result = data.get('result')
                if not isinstance(result, list):
                    print(f"获取到的result不是列表类型: {type(result)}")
                    time.sleep(5)
                    continue

                updates = result

            except Exception as e:
                print(f"获取更新失败: {e}")
                print(traceback.format_exc())
                time.sleep(5)
                continue

            # 处理每条消息
            if not updates:
                continue

            for update in updates:
                try:
                    message = update.get("message", {})
                    if not message:
                        continue

                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")

                    if not text:
                        continue

                    if text == "/start":
                        name = message.get("from", {}).get("first_name", "")
                        welcome_message = (f"Benvenuto {name}, mandami il link amazon di un prodotto per "
                                        "creare il post sul tuo canale!")
                        send_telegram_message(chat_id, welcome_message)
                    elif "amazon." in text and ("/dp/" in text or "/gp/product/" in text):
                        handle_amazon_link(text)

                    last_update_id = update["update_id"] + 1

                except Exception as e:
                    print(f"处理消息时出错: {e}")
                    print(traceback.format_exc())
                    continue

        except KeyboardInterrupt:
            print("\n停止机器人...")
            break
        except Exception as e:
            print(f"主循环出错: {e}")
            print(traceback.format_exc())
            time.sleep(5)

if __name__ == '__main__':
    main()
