import os
import time
import threading
import requests
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- بيانات بوت إسبانيا ---
TELEGRAM_TOKEN = "8985660641:AAEYNMhKxqt3ZEshI2RwJEcB1g0nhlD8iEw"
TELEGRAM_CHAT_ID = "8274522042"
BLS_URL = "https://algeria.blsspainvisa.com/"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        # استخدام json=payload بدلاً من data=payload لتفادي رفض تيليجرام للطلب
        response = requests.post(url, json=payload, timeout=10)
        print(f"استجابة تيليجرام: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"خطأ أثناء إرسال رسالة تيليجرام: {e}")

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

            # البحث عن عناصر المواعيد المتاحة في موقع BLS
            available_slots = page.query_selector_all('.day:not(.disabled), .appointment-slot:not(.booked)')

            if len(available_slots) > 0:
                send_telegram("🚨 عاجل ومؤكد: تم العثور على موعد متاح الآن في موقع BLS إسبانيا! ادخل واحجز فوراً.")
        except Exception as e:
            print(f"خطأ أثناء فحص مواعيد إسبانيا: {e}")
        finally:
            browser.close()

def run_loop():
    # إرسال رسالة الترحيب والبدء عند تشغيل السكريبت
    send_telegram("✅ تم تشغيل سكريبت مراقبة مواعيد إسبانيا بنجاح على Render (24/7)!")
    while True:
        check_spain_appointments()
        time.sleep(900)  # إعادة الفحص كل 15 دقيقة (900 ثانية)

@app.route('/')
def home():
    return "Spain Visa Bot is Running 24/7!"

if __name__ == '__main__':
    # تشغيل حلقات المراقبة في خلفية خادم Flask
    t = threading.Thread(target=run_loop)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
