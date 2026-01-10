import os, time, subprocess, threading, telebot
from flask import Flask

# --- الإعدادات ---
TOKEN = '7957457845:AAGTe2_4avne8h5MxZCnEY8lCzACOTBKKxo'
ADMIN_ID = 5747051433
# رابط البث
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

bot = telebot.TeleBot(TOKEN)
is_running = False
file_counter = 1
ffmpeg_process = None

# سيرفر ويب لضمان استمرارية الخدمة على Render
app = Flask(__name__)
@app.route('/')
def health(): return "Recording Bot is Online", 200

# دالة إرسال المقاطع المسجلة
def send_worker():
    global file_counter
    while True:
        if is_running:
            # البحث عن الملفات التي تم الانتهاء من تسجيلها
            files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
            # نترك آخر ملف لأنه قد يكون قيد الكتابة حالياً
            if len(files) > 1:
                f_name = files[0]
                try:
                    with open(f_name, 'rb') as v:
                        bot.send_video(ADMIN_ID, v, caption=f"🎥 مقطع جديد رقم: {file_counter}")
                    os.remove(f_name)
                    file_counter += 1
                except Exception as e:
                    print(f"Error sending file: {e}")
        time.sleep(2)

# أمر بدأ التسجيل
@bot.message_handler(commands=['startlive'])
def start_live(message):
    global is_running, file_counter, ffmpeg_process
    if message.chat.id == ADMIN_ID:
        if not is_running:
            is_running = True
            file_counter = 1
            bot.reply_to(message, "🎬 تم بدأ تسجيل البث بنجاح..")
            # تشغيل FFmpeg في Thread منفصل
            threading.Thread(target=run_ffmpeg, daemon=True).start()
        else:
            bot.reply_to(message, "⚠️ التسجيل يعمل بالفعل.")

# أمر إيقاف التسجيل
@bot.message_handler(commands=['stoplive'])
def stop_live(message):
    global is_running, ffmpeg_process
    if message.chat.id == ADMIN_ID:
        if is_running:
            is_running = False
            if ffmpeg_process:
                ffmpeg_process.terminate() # إيقاف عملية FFmpeg
            bot.reply_to(message, "🛑 تم إيقاف التسجيل.")
            # تنظيف الملفات المتبقية
            for f in os.listdir('.'):
                if f.startswith('seg_'): os.remove(f)
        else:
            bot.reply_to(message, "⚠️ لا يوجد تسجيل يعمل حالياً.")

def run_ffmpeg():
    global ffmpeg_process
    # تقسيم البث إلى مقاطع مدتها 21 ثانية
    cmd = [
        'ffmpeg', '-i', URL, 
        '-c', 'copy', 
        '-f', 'segment', 
        '-segment_time', '21', 
        '-reset_timestamps', '1', 
        'seg_%03d.mp4'
    ]
    ffmpeg_process = subprocess.Popen(cmd)
    ffmpeg_process.wait()

if __name__ == "__main__":
    # تشغيل العامل المسؤول عن الإرسال
    threading.Thread(target=send_worker, daemon=True).start()
    # تشغيل سيرفر الويب
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    # تشغيل استقبال أوامر البوت
    print("Bot is running...")
    bot.polling(non_stop=True)
