from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    """健康检查端点"""
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    """处理Telegram webhook请求"""
    try:
        # 简单的响应测试
        return JSONResponse(content={"ok": True, "message": "Webhook endpoint is working"})
    except Exception as e:
        return JSONResponse(
            content={"ok": False, "error": str(e)},
            status_code=500
        )

# Vercel需要的handler
handler = app
