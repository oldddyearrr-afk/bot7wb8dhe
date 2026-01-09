import os, time, subprocess, threading, queue, telebot, signal
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- إعدادات البوت ---
TOKEN = '8001928461:AAEckKw5lfZiQR1cAoLCeSwWoVWIAylj3uc'
ID = 5747051433
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

bot = telebot.TeleBot(TOKEN)
is_running = False
ffmpeg_process = None
file_counter = 1  # عداد لإعطاء ID لكل مقطع

# --- خادم وهمي لإرضاء Render ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Control is Active!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- تنظيف الملفات المتراكمة ---
def clean_files():
    files = [f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')]
    for f in files:
        try: os.remove(f)
        except: pass
    print("🧹 Storage Cleaned.")

# --- خيط الإرسال مع نظام الـ ID ---
def snd_worker():
    global file_counter
    while True:
        if is_running:
            # البحث عن الملفات المسجلة
            files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
            # نرسل الملف فقط إذا ظهر ملف جديد (أي أن الحالي اكتمل)
            if len(files) > 1:
                f_name = files[0]
                try:
                    with open(f_name, 'rb') as v:
                        # إرسال الفيديو لك مع الـ ID في الوصف
                        bot.send_video(ID, v, caption=f"🎥 مقطع جديد\n🆔 ID: {file_counter}", timeout=60)
                    
                    os.remove(f_name)
                    file_counter += 1 # زيادة العداد للمقطع القادم
                except Exception as e:
                    print(f"Error sending: {e}")
        time.sleep(2)

# --- معالجة الأوامر ---
@bot.message_handler(commands=['startlive'])
def start_live(message):
    global is_running, file_counter
    if message.chat.id != ID: return
    if not is_running:
        file_counter = 1 # إعادة تصفير العداد عند كل بداية جديدة
        is_running = True
        bot.reply_to(message, "🎬 تم بدء التسجيل. سأرسل المقاطع مع ID لكل منها...")
        threading.Thread(target=rec_worker, daemon=True).start()
    else:
        bot.reply_to(message, "⚠️ البث شغال بالفعل!")

@bot.message_handler(commands=['stoplive'])
def stop_live(message):
    global is_running, ffmpeg_process
    if message.chat.id != ID: return
    is_running = False
    if ffmpeg_process:
        ffmpeg_process.terminate()
        ffmpeg_process = None
    clean_files()
    bot.reply_to(message, "🛑 تم إيقاف البث وتنظيف المساحة.")

def rec_worker():
    global ffmpeg_process
    # استخدام نظام الأجزاء لضمان عدم تفويت ثانية واحدة
    cmd = ['ffmpeg', '-i', URL, '-c', 'copy', '-f', 'segment', '-segment_time', '21', '-reset_timestamps', '1', 'seg_%03d.mp4']
    while is_running:
        ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ffmpeg_process.wait()
        if not is_running: break
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=snd_worker, daemon=True).start()
    print("🤖 Bot is waiting for commands...")
    bot.polling(non_stop=True)
