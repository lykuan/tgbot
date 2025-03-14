# Amazon Telegram Bot

这是一个用于处理Amazon链接并发送到Telegram频道的机器人。

## 部署到Vercel

1. 首先确保你有一个Vercel账号，如果没有请在 [Vercel](https://vercel.com) 注册

2. 安装Vercel CLI:
```bash
npm i -g vercel
```

3. 登录Vercel:
```bash
vercel login
```

4. 在项目根目录运行:
```bash
vercel
```

5. 部署完成后，你会得到一个类似 `https://your-project.vercel.app` 的URL

## 设置Telegram Webhook

1. 替换以下URL中的内容：
   - 将 `YOUR_BOT_TOKEN` 替换为你的Telegram机器人token
   - 将 `YOUR_VERCEL_URL` 替换为Vercel给你的URL

```
https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=YOUR_VERCEL_URL/webhook
```

2. 在浏览器中访问这个URL来设置webhook

3. 如果成功，你会看到类似这样的响应：
```json
{
    "ok": true,
    "result": true,
    "description": "Webhook was set"
}
```

## 环境变量设置

在Vercel仪表板中，你需要设置以下环境变量：

1. `TELEGRAM_TOKEN`: 你的Telegram Bot Token
2. `CHANNEL_ID`: 目标Telegram频道ID

设置步骤：
1. 进入你的Vercel项目
2. 点击 "Settings"
3. 选择 "Environment Variables"
4. 添加上述环境变量

## 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务器：
```bash
uvicorn web_bot:app --reload
```

服务器将在 `http://localhost:8000` 运行。

## 注意事项

1. 确保你的Telegram机器人有足够的权限发送消息到目标频道
2. 建议在正式部署前在本地测试机器人功能
3. 如果遇到问题，可以查看Vercel的日志来排查问题

## API文档

部署后可以访问 `/docs` 或 `/redoc` 路径查看API文档（由FastAPI自动生成）。
