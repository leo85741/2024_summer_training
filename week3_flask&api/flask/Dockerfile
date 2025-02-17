FROM python:3.9-slim

# 工作目錄
WORKDIR /app

# 安裝 Tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY . /app

# 從python的host 安裝需要的套件
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# 開放容器的port:80
EXPOSE 8000

# 環境變數
# ENV NAME World

# Run app.py
CMD ["python", "api_test.py"]
