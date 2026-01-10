import os, time, subprocess, threading, telebot
from flask import Flask

# --- الإعدادات ---
TOKEN = '7957457845:AAGTe2_4avne8h5MxZCnEY8lCzACOTBKKxo'
MERGE_BOT_TOKEN = '8237586935:AAFCfvGqx5KWuXGwyyECS_flh-V4fulCUGg'
ADMIN_ID = 5747051433
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

bot = telebot.TeleBot(TOKEN)
merge_bot = telebot.TeleBot(MERGE_BOT_TOKEN)
is_running = False
file_counter = 1

# سيرفر ويب خفيف جداً لـ Render
app = Flask(__name__)
@app.route('/')
def health(): return "Recording Bot Active", 200

def snd_worker():
    global file_counter
    while True:
        if is_running:
            files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
            if len(files) > 1:
                f_name = files[0]
                try:
                    with open(f_name, 'rb') as v:
                        # إرسال لك وللبوت الثاني فوراً
                        bot.send_video(ADMIN_ID, v, caption=f"🎥 مقطع {file_counter}")
                        v.seek(0)
                        merge_bot.send_document(ADMIN_ID, v, caption=f"SAVE:{file_counter}")
                    os.remove(f_name)
                    file_counter += 1
                except: pass
        time.sleep(1)

@bot.message_handler(commands=['startlive'])
def start(message):
    global is_running, file_counter
    if message.chat.id == ADMIN_ID:
        file_counter = 1
        is_running = True
        bot.reply_to(message, "🎬 بدأ التسجيل...")
        threading.Thread(target=rec_worker, daemon=True).start()

def rec_worker():
    cmd = ['ffmpeg', '-i', URL, '-c', 'copy', '-f', 'segment', '-segment_time', '21', '-reset_timestamps', '1', 'seg_%03d.mp4']
    subprocess.run(cmd)

if __name__ == "__main__":
    threading.Thread(target=snd_worker, daemon=True).start()
    # تشغيل السيرفر على المنفذ المطلوب من Render
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    bot.polling(non_stop=True)
