import os, time, subprocess, threading, queue, telebot
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- إعدادات البوت ---
TOKEN = '8001928461:AAEckKw5lfZiQR1cAoLCeSwWoVWIAylj3uc'
ID = 5747051433
URL = 'http://g.cuminx.xyz/SOFIANBENAISSA/X7KJL94/1339213?token=ShN0YQ0JGlhBVEk9ShAWG04kBi5fWQJEC0E8WgsHJDJHQQQJQQQQQ1JHG0EQQQQQQQ0QQQ0UWwVQAVVQUwxNQ0QQQQQQQQxAWUcQAQQQQQQQRhVGQQQQQUcNUFJQDFFQBQQACEgSQQQQRw1BQQQHQQQQQEYcFAQQQQQQQQQQQQQQQQQQQRICDBYJW09EV1xnBQFUBV5SQw5HBkNJRAQQQRMLXEQIXB.RAAQxDEQdMVxpbRghcBwBDGEdUDhAITRMYEwsQdSESFEAGHUMGCEtbVw9GA0ZERUMYR14SOhRcEhVDVFNcAUIaWEFVFU9EVVNAPgdWCl5TAkAMQQQQRANDQBMdEFQQQQQQAQQQEQQQEAJDQQQQQQQQQ0dK'

bot = telebot.TeleBot(TOKEN)
q = queue.Queue()

# --- خادم وهمي لإرضاء Render ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Live!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- دوام الإرسال والتسجيل ---
def snd():
    while True:
        files = sorted([f for f in os.listdir('.') if f.startswith('seg_') and f.endswith('.mp4')])
        if len(files) > 1:
            f = files[0]
            try:
                with open(f, 'rb') as v:
                    bot.send_video(ID, v, timeout=60)
                os.remove(f)
                print(f'✅ Sent: {f}')
            except:
                time.sleep(2)
        time.sleep(1)

def rec():
    cmd = ['ffmpeg', '-i', URL, '-c', 'copy', '-f', 'segment', '-segment_time', '21', '-reset_timestamps', '1', 'seg_%03d.mp4']
    subprocess.run(cmd)

if __name__ == "__main__":
    # تشغيل الخادم الوهمي في خيط منفصل
    threading.Thread(target=run_server, daemon=True).start()
    # تشغيل الإرسال في خيط منفصل
    threading.Thread(target=snd, daemon=True).start()
    # تشغيل التسجيل
    rec()
