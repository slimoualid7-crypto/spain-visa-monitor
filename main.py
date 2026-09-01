import os
import time
import threading
import requests
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- بيانات بوت إسبانيا الجديد ---
TELEGRAM_TOKEN = "8985660641:AAEYNMhKxqt3ZEShi2RwJEcBlq0nhldBiEw"
TELEGRAM_CHAT_ID = "8274522042"
BLS_URL = "https://algeria.blsspainvisa.com/"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ تيليجرام: {e}")

def check_spain_appointments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            page.goto(BLS_URL, timeout=60000)
            page.wait_for_timeout(3000)

            # فحص المواعيد المتاحة
            available_slots = page.query_selector_all('.day:not(.disabled), .appointment-slot:not(.booked)')

            if len(available_slots) > 0:
                send_telegram("🚨 عاجل ومؤكد: تم العثور على موعد متاح الآن في موقع BLS إسبانيا! ادخل واحجز فوراً.")
        except Exception as e:
            print(f"خطأ أثناء الفحص: {e}")
        finally:
            browser.close()

def run_loop():
    send_telegram("✅ تم تشغيل سكريبت مراقبة مواعيد إسبانيا بنجاح على Render (24/7)!")
    while True:
        check_spain_appointments()
        time.sleep(900)  # إعادة الفحص كل 15 دقيقة

@app.route('/')
def home():
    return "Spain Visa Bot is Running 24/7!"

if __name__ == '__main__':
    # تشغيل الفحص في خلفية خادم Flask لربط المنفذ والحفاظ على الخدمة حية 24/7
    t = threading.Thread(target=run_loop)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
