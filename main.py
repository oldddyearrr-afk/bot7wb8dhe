import os
import time
import subprocess
import threading
import queue
import telebot

# بيانات البوت والبث
TOKEN = '8001928461:AAEckKw5lfZiQR1cAoLCeSwWoVWIAylj3uc'
ID = 5747051433
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

q = queue.Queue()
bot = telebot.TeleBot(TOKEN)

def snd():
    while True:
        # البحث عن الملفات التي تبدأ بـ seg_ وتنتهي بـ .mp4
        files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
        
        # إذا كان هناك أكثر من ملف، نرسل الأقدم ونترك الأحدث (الذي يتم تسجيله حالياً)
        if len(files) > 1:
            file_to_send = files[0]
            try:
                with open(file_to_send, 'rb') as v:
                    bot.send_video(ID, v, timeout=60)
                print(f"✅ Sent and Deleted: {file_to_send}")
            except Exception as e:
                print(f"❌ Error sending {file_to_send}: {e}")
            
            # حذف الملف في كل الأحوال (سواء أُرسل أو فشل) لحماية المساحة
            if os.path.exists(file_to_send):
                os.remove(file_to_send)
        
        # حماية إضافية: إذا تراكمت ملفات لأي سبب، امسحها فوراً
        if len([f for f in os.listdir('.') if f.startswith('seg_')]) > 5:
            for extra_file in files[:-1]:
                os.remove(extra_file)
                
        time.sleep(2)

def rec():
    # استخدام ffmpeg بنظام الأجزاء (segment) لضمان عدم تفويت أي ثانية
    cmd = [
        'ffmpeg', '-i', URL,
        '-c', 'copy',
        '-f', 'segment',
        '-segment_time', '21',
        '-reset_timestamps', '1',
        'seg_%03d.mp4'
    ]
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"⚠️ FFmpeg Error: {e}")
        time.sleep(5)
        rec() # إعادة المحاولة في حال الانقطاع

if __name__ == "__main__":
    # إشعار البدء
    try: bot.send_message(ID, "🚀 البوت بدأ العمل على سيرفر Render!")
    except: pass
    
    # تشغيل خيط الإرسال
    threading.Thread(target=snd, daemon=True).start()
    # تشغيل التسجيل في الخيط الرئيسي
    rec()
