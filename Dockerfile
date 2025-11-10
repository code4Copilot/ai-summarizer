FROM python:3.10-slim

# 工作目錄
WORKDIR /app

# 避免產生 pyc 並讓輸出非緩衝
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 複製並安裝相依套件
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 複製應用程式程式碼
COPY . /app

# 開放 Gradio 預設埠號
EXPOSE 7860

# 預設啟動指令：執行 main.py（Gradio 介面）
CMD ["python", "main.py"]