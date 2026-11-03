import os
import threading
from flask import Flask
import telebot
import requests

# --- تنظیمات از Environment Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "xingchen-agi/xing4.0-29b-a4b:free")

# --- ربات تلگرام ---
bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_PROMPT = """تو منشی شخصی من هستی. کوتاه، مودب و کاربردی به فارسی جواب بده.
اگر کاربر گفت یادآور بذار، بگو 'ثبت شد' و جزئیات رو تکرار کن."""

def ask_ai(user_text):
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
            },
            timeout=60,
        )
        data = r.json()

        # --- چک کردن خطای واقعی ---
        if "error" in data:
            return f"خطای OpenRouter: {data['error']}"
        if "choices" not in data or not data["choices"]:
            return f"پاسخ نامعتبر: {data}"

        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطا در ارتباط با هوش مصنوعی: {e}"
        
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
    bot.reply_to(msg, ask_ai(msg.text))

# --- اجرای همزمان وب‌سرور و ربات ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
