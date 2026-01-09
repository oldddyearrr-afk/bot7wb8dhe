# استخدام نسخة بايثون خفيفة
FROM python:3.11-slim

# تثبيت FFmpeg وتحديث النظام داخل الحاوية
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات الكود
COPY . .

# تشغيل البوت
CMD ["python", "main.py"]
