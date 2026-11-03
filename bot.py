import os
import threading
from flask import Flask
import telebot
import requests

# --- تنظیمات از Environment Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
# لیست مدل‌های رایگان به ترتیب اولویت (اگر یکی محدود شد، بعدی امتحان می‌شه)
FREE_MODELS = [
    os.getenv("MODEL_NAME", "xingchen-agi/xing4.0-29b-a4b:free"),
    "moonshotai/kimi-k2.5:free",
    "google/gemma-4-31b-it:free",
]

# --- ربات تلگرام ---
bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_PROMPT = """تو منشی شخصی من هستی. کوتاه، مودب و کاربردی به فارسی جواب بده.
اگر کاربر گفت یادآور بذار، بگو 'ثبت شد' و جزئیات رو تکرار کن."""

def ask_ai(user_text):
    last_error = None
    for model in FREE_MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_text},
                    ],
                },
                timeout=60,
            )
            data = r.json()

            # اگر خطا داشت
            if "error" in data:
                err_code = data["error"].get("code")
                last_error = f"[{model}] {data['error']}"
                # اگر 429 یا خطای موقت بود، برو مدل بعدی
                if err_code in (429, 503, 502):
                    continue
                # خطای جدی (مثل 401) → برگردون
                return f"خطای OpenRouter: {data['error']}"

            if "choices" not in data or not data["choices"]:
                last_error = f"[{model}] پاسخ نامعتبر: {data}"
                continue

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            last_error = f"[{model}] {e}"
            continue

    return f"همه مدل‌ها در دسترس نیستن. آخرین خطا:\n{last_error}"
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
