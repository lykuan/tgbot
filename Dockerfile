FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY *.py .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 添加httpx依赖
RUN pip install --no-cache-dir httpx

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "web_bot:app", "--host", "0.0.0.0", "--port", "8000"]
