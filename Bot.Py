import os
import threading
from flask import Flask
import telebot
import google.generativeai as genai

# --- تنظیمات از Environment Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# --- ربات تلگرام ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- مدل هوش مصنوعی ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """تو منشی شخصی من هستی. کوتاه، مودب و کاربردی جواب بده.
اگر کاربر گفت یادآور بذار، بگو 'ثبت شد' و جزئیات رو تکرار کن."""

# --- وب‌سرور ساده برای Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Rumi Admin Bot is running ✅"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- هندلرهای تلگرام ---
@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(msg, "سلام! من منشی شما هستم. چطور کمکتون کنم؟")

@bot.message_handler(func=lambda m: True)
def handle(msg):
    try:
        resp = model.generate_content(f"{SYSTEM_PROMPT}\n\nکاربر: {msg.text}")
        bot.reply_to(msg, resp.text)
    except Exception as e:
        bot.reply_to(msg, f"خطا: {e}")

# --- اجرای همزمان وب‌سرور و ربات ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
