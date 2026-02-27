import os
import requests
from pathlib import Path


env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

token = os.getenv('BOT_TOKEN', '').strip()
chat_id = os.getenv('CHAT_ID', '').strip()

print("=" * 50)
print("🔍 تست اتصال ربات تلگرام")
print("=" * 50)
print(f"BOT_TOKEN: {token[:20]}...{token[-10:] if len(token) > 30 else ''}")
print(f"CHAT_ID: {chat_id}")
print("=" * 50)

if not token or not chat_id:
    print("❌ خطا: BOT_TOKEN یا CHAT_ID خالی است!")
    print("لطفاً فایل .env را بررسی کنید")
    exit(1)

# تست 1: بررسی اعتبار توکن
print("\n📡 تست 1: بررسی اعتبار توکن...")
try:
    response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"✅ توکن معتبر است")
        print(f"   نام ربات: @{bot_info['username']}")
        print(f"   نام نمایشی: {bot_info['first_name']}")
    else:
        print(f"❌ توکن نامعتبر است: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ خطا در اتصال: {e}")
    exit(1)

print("\n📤 تست 2: ارسال پیام تست...")
try:
    payload = {
        "chat_id": chat_id,
        "text": "🧪 <b>پیام تست</b>\n\nاگر این پیام را می‌بینید، ربات شما به درستی کار می‌کند! ✅",
        "parse_mode": "HTML"
    }
    
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ پیام با موفقیت ارسال شد!")
        print("   لطفاً ربات خود را در تلگرام چک کنید")
    else:
        print(f"❌ خطا در ارسال پیام:")
        print(f"   کد خطا: {response.status_code}")
        print(f"   پیام خطا: {response.text}")
        
        # راهنمایی برای خطاهای رایج
        if response.status_code == 400:
            print("\n💡 احتمالاً CHAT_ID اشتباه است")
            print("   - مطمئن شوید که به ربات پیام /start داده‌اید")
            print("   - CHAT_ID را از getUpdates دوباره بگیرید")
        elif response.status_code == 401:
            print("\n💡 BOT_TOKEN اشتباه است")
            print("   - توکن را از @BotFather دوباره بگیرید")
            
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("تست تمام شد")
print("=" * 50)
