import os, time, subprocess, threading, queue, telebot, signal
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- إعدادات البوت ---
TOKEN = '8001928461:AAEckKw5lfZiQR1cAoLCeSwWoVWIAylj3uc'
ID = 5747051433
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

bot = telebot.TeleBot(TOKEN)
is_running = False
ffmpeg_process = None

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

# --- خيط الإرسال ---
def snd_worker():
    while True:
        if is_running:
            files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
            if len(files) > 1:
                f = files[0]
                try:
                    with open(f, 'rb') as v:
                        bot.send_video(ID, v, timeout=60)
                    os.remove(f)
                except: pass
        time.sleep(2)

# --- معالجة الأوامر ---
@bot.message_handler(commands=['startlive'])
def start_live(message):
    global is_running, ffmpeg_process
    if message.chat.id != ID: return
    if not is_running:
        is_running = True
        bot.reply_to(message, "🎬 تم بدء التسجيل والبث المباشر...")
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
    bot.reply_to(message, "🛑 تم إيقاف البث وتنظيف المساحة بنجاح.")

def rec_worker():
    global ffmpeg_process
    cmd = ['ffmpeg', '-i', URL, '-c', 'copy', '-f', 'segment', '-segment_time', '21', '-reset_timestamps', '1', 'seg_%03d.mp4']
    while is_running:
        ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ffmpeg_process.wait()
        if not is_running: break
        time.sleep(5)

if __name__ == "__main__":
    # تشغيل الخدمات الخلفية
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=snd_worker, daemon=True).start()
    print("🤖 Bot is waiting for commands...")
    bot.polling(non_stop=True)
