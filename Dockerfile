# استخدام نسخة Alpine خفيفة جداً
FROM python:3.11-alpine

# تثبيت FFmpeg بأقل حجم ممكن وتحديث الشهادات
RUN apk add --no-cache ffmpeg

# تحديد مجلد العمل
WORKDIR /app

# تثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# تشغيل البوت
CMD ["python", "main.py"]
