import os, time, subprocess, threading, queue, telebot, signal
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- إعدادات البوت ---
TOKEN = '7957457845:AAGTe2_4avne8h5MxZCnEY8lCzACOTBKKxo'
ID = 5747051433
URL = 'https://rmtv.akamaized.net/hls/live/2043153/rmtv-es-web/bitrate_3.m3u8'

bot = telebot.TeleBot(TOKEN)
is_running = False
ffmpeg_process = None

# قائمة لتخزين الأيديهات (تبدأ بالأونر)
target_ids = {ID}

# --- خادم ويب لإرضاء Render (فتح البورت) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is Running and Port is Open!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"🌍 Server listening on port {port}")
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
                        video_data = v.read()
                    
                    # الإرسال لجميع الأيديهات المضافة
                    for target in list(target_ids):
                        try:
                            bot.send_video(target, video_data, timeout=60)
                        except: pass
                    
                    os.remove(f)
                except: pass
        time.sleep(2)

# --- معالجة الأوامر ---

@bot.message_handler(commands=['setlive'])
def set_live(message):
    if message.chat.id != ID: return
    msg = bot.reply_to(message, "🔗 من فضلك أرسل رابط البث الجديد الآن (m3u8, ts, mpd):")
    bot.register_next_step_handler(msg, update_url)

def update_url(message):
    global URL
    new_url = message.text
    if new_url.startswith('http'):
        URL = new_url
        bot.reply_to(message, f"✅ تم تحديث رابط البث بنجاح إلى:\n{URL}")
    else:
        bot.reply_to(message, "❌ الرابط غير صحيح، يرجى البدء بـ http أو https.")

@bot.message_handler(commands=['multilive'])
def multi_live(message):
    if message.chat.id != ID: return
    msg = bot.reply_to(message, "👤 من فضلك أرسل (ID) الشخص الذي تريد إضافته:")
    bot.register_next_step_handler(msg, add_id)

def add_id(message):
    try:
        new_id = int(message.text)
        target_ids.add(new_id)
        bot.reply_to(message, f"✅ تم إضافة الأيدي {new_id} لقاعدة بيانات الإرسال.")
    except:
        bot.reply_to(message, "❌ خطأ! يرجى إرسال رقم الأيدي بشكل صحيح.")

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
    # تحسين الاتصال ليدعم m3u8, mpd, ts مع معالجة الانقطاع
    cmd = [
        'ffmpeg', 
        '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5', # لإعادة الاتصال تلقائياً
        '-i', URL, 
        '-c', 'copy', 
        '-f', 'segment', 
        '-segment_time', '21', 
        '-reset_timestamps', '1', 
        '-segment_format_options', 'movflags=+faststart', # لضمان تشغيل الفيديو فور وصوله للتليجرام
        'seg_%03d.mp4'
    ]
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
