import os, time, subprocess, threading, telebot
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
TOKEN = '8001928461:AAEckKw5lfZiQR1cAoLCeSwWoVWIAylj3uc'
MERGE_BOT_TOKEN = '7867778362:AAHtvj9wOAHpG9BPcGPEqNIkT2O5DLXtIPI'
ID = 5747051433
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

bot = telebot.TeleBot(TOKEN)
merge_bot = telebot.TeleBot(MERGE_BOT_TOKEN)

is_running = False
ffmpeg_process = None
file_counter = 1

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Recording Server Active")

def snd_worker():
    global file_counter
    while True:
        if is_running:
            files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
            if len(files) > 1:
                f_name = files[0]
                caption_text = f"ID:{file_counter}"
                try:
                    with open(f_name, 'rb') as v:
                        # إرسال فيديو لك للمشاهدة
                        bot.send_video(ID, v, caption=f"🎥 مقطع {file_counter}")
                        # إرسال مستند لبوت الدمج (هذا الجزء يضمن الحفظ في السيرفر الآخر)
                        v.seek(0)
                        merge_bot.send_document(ID, v, caption=caption_text)
                    
                    os.remove(f_name)
                    file_counter += 1
                except: pass
        time.sleep(2)

@bot.message_handler(commands=['startlive'])
def start_live(message):
    global is_running, file_counter
    if message.chat.id == ID:
        file_counter = 1
        is_running = True
        bot.reply_to(message, "🎬 بدأ التسجيل.. انتظر رسائل التأكيد من بوت الدمج.")
        threading.Thread(target=rec_worker, daemon=True).start()

@bot.message_handler(commands=['stoplive'])
def stop_live(message):
    global is_running, ffmpeg_process
    if message.chat.id == ID:
        is_running = False
        if ffmpeg_process: ffmpeg_process.terminate()
        bot.reply_to(message, "🛑 توقف التسجيل.")

def rec_worker():
    global ffmpeg_process
    cmd = ['ffmpeg', '-i', URL, '-c', 'copy', '-f', 'segment', '-segment_time', '21', '-reset_timestamps', '1', 'seg_%03d.mp4']
    while is_running:
        ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ffmpeg_process.wait()
        if not is_running: break
        time.sleep(5)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', port), SimpleHandler).serve_forever(), daemon=True).start()
    threading.Thread(target=snd_worker, daemon=True).start()
    bot.polling(non_stop=True)
