FROM python:3.11-slim

# تثبيت أداة FFmpeg وتحديث النظام
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# تشغيل البوت
CMD ["python", "main.py"]
