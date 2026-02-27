import os
import time
import requests
import threading
from datetime import datetime, timedelta
from pathlib import Path

class ClassReminder:
    def __init__(self):
        self.load_env()
        self.load_config()
        self.confirmed_alerts = {}
        self.offset = None
        self.running = True
        
    def load_env(self):
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            with open(env_path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        
        self.token = os.getenv('BOT_TOKEN', '').strip()
        self.chat_id = os.getenv('CHAT_ID', '').strip()
        
        if not self.token or not self.chat_id:
            raise ValueError("BOT_TOKEN و CHAT_ID باید در فایل .env تنظیم شوند")
    
    def load_config(self):
        self.classes = [
            {"day": "Friday", "start": "03:19", "end": "5:25", "name": "ریاضی عمومی"},
            {"day": "Saturday", "start": "14:30", "end": "18:30", "name": "طراحی و ..."},
            {"day": "Sunday", "start": "13:30", "end": "15:30", "name": "اندیشه اسلامی"},
            {"day": "Sunday", "start": "17:30", "end": "19:30", "name": "زبان فنی"},
            {"day": "Monday", "start": "07:30", "end": "09:30", "name": "آزمایشگاه نرم‌افزار"},
            {"day": "Monday", "start": "13:30", "end": "15:30", "name": "پایگاه داده‌ها"},
            {"day": "Monday", "start": "15:30", "end": "17:30", "name": "مهارت‌های تصمیم‌گیری"},
            {"day": "Tuesday", "start": "07:30", "end": "09:30", "name": "تربیت بدنی"},
            {"day": "Tuesday", "start": "09:30", "end": "11:30", "name": "آزمایشگاه سیستم عامل"},
            {"day": "Tuesday", "start": "11:30", "end": "14:30", "name": "کارگاه شبکه"},
            {"day": "Tuesday", "start": "14:30", "end": "18:30", "name": "برنامه‌نویسی موبایل"}
        ]
        self.alert_minutes = 10
        self.reminder_interval = 60
    
    def send_message(self, text, keyboard=None):
        try:
            import urllib3
            urllib3.disable_warnings()
            
            payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
            if keyboard:
                payload["reply_markup"] = keyboard
            
            print(f"🔄 در حال ارسال پیام به chat_id: {self.chat_id}")
            
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json=payload,
                timeout=60,
                verify=True
            )
            
            if response.status_code == 200:
                print(f"✅ پیام با موفقیت ارسال شد")
                return True
            else:
                print(f"❌ خطا {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ خطا در ارسال: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
 
    
    def get_updates(self):
        try:
            params = {"timeout": 5}
            if self.offset:
                params["offset"] = self.offset
            
            response = requests.get(
                f"https://api.telegram.org/bot{self.token}/getUpdates",
                params=params,
                timeout=10
            )
            return response.json().get("result", [])
        except:
            return []
    
    def process_updates(self):
        while self.running:
            try:
                updates = self.get_updates()
                for update in updates:
                    self.offset = update["update_id"] + 1
                    
                    if "callback_query" in update:
                        callback = update["callback_query"]
                        data = callback.get("data", "")
                        
                        if data.startswith("confirm_"):
                            alert_key = data.replace("confirm_", "")
                            if alert_key in self.confirmed_alerts:
                                self.confirmed_alerts[alert_key] = True
                                
                                requests.post(
                                    f"https://api.telegram.org/bot{self.token}/answerCallbackQuery",
                                    json={"callback_query_id": callback["id"], "text": "✅ تایید شد"},
                                    timeout=5
                                )
                                
                                requests.post(
                                    f"https://api.telegram.org/bot{self.token}/editMessageText",
                                    json={
                                        "chat_id": self.chat_id,
                                        "message_id": callback["message"]["message_id"],
                                        "text": callback["message"]["text"] + "\n\n✅ <b>تایید شد</b>",
                                        "parse_mode": "HTML"
                                    },
                                    timeout=5
                                )
                
                time.sleep(1)
            except Exception as e:
                print(f"خطا در پردازش: {e}")
                time.sleep(5)
    
    def get_alert_key(self, cls, date):
        start_time = datetime.strptime(cls['start'], "%H:%M").replace(
            year=date.year, month=date.month, day=date.day
        )
        return f"{date.strftime('%Y-%m-%d')}-{cls['name']}-{start_time.strftime('%H:%M')}"
    
    def check_classes(self):
        while self.running:
            try:
                now = datetime.now()
                current_day = now.strftime("%A")
                
                for cls in self.classes:
                    if cls['day'] != current_day:
                        continue
                    
                    alert_key = self.get_alert_key(cls, now)
                    
                    if alert_key in self.confirmed_alerts:
                        continue
                    
                    start_time = datetime.strptime(cls['start'], "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day
                    )
                    
                    alert_time = start_time - timedelta(minutes=self.alert_minutes)
                    
                    if alert_time <= now < start_time:
                        self.confirmed_alerts[alert_key] = False
                        threading.Thread(
                            target=self.handle_alert,
                            args=(cls, alert_key, start_time),
                            daemon=True
                        ).start()
                
                self.cleanup_old_alerts(now)
                time.sleep(30)
                
            except Exception as e:
                print(f"خطا در چک کلاس‌ها: {e}")
                time.sleep(5)
    
    def handle_alert(self, cls, alert_key, start_time):
        now = datetime.now()
        time_until = int((start_time - now).total_seconds() / 60)
        
        message = (
            f"🔔 <b>یادآور کلاس</b>\n\n"
            f"📚 <b>{cls['name']}</b>\n"
            f"🕐 زمان شروع: <code>{cls['start']}</code>\n"
            f"⏱ باقیمانده: <b>{time_until} دقیقه</b>\n\n"
            f"لطفاً حضور خود را تایید کنید 👇"
        )
        
        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ تایید حضور", "callback_data": f"confirm_{alert_key}"}
            ]]
        }
        
        self.send_message(message, keyboard)
        print(f"{now.strftime('%H:%M:%S')} - هشدار {cls['name']} ارسال شد")
        
        last_reminder = datetime.now()
        
        while not self.confirmed_alerts.get(alert_key, False):
            if datetime.now() >= start_time:
                print(f"{datetime.now().strftime('%H:%M:%S')} - کلاس {cls['name']} شروع شد")
                # حذف alert_key تا بتوان بعد از شروع کلاس هم تایید کرد
                # اگر نخواهید این قابلیت را داشته باشید، خط بعدی را uncomment کنید:
                # del self.confirmed_alerts[alert_key]
                break
            
            if (datetime.now() - last_reminder).total_seconds() >= self.reminder_interval:
                time_until = int((start_time - datetime.now()).total_seconds() / 60)
                reminder_msg = (
                    f"⚠️ <b>یادآوری مجدد</b>\n\n"
                    f"📚 <b>{cls['name']}</b>\n"
                    f"⏱ فقط <b>{time_until} دقیقه</b> مانده!\n\n"
                    f"لطفاً حضور خود را تایید کنید 👇"
                )
                self.send_message(reminder_msg, keyboard)
                print(f"{datetime.now().strftime('%H:%M:%S')} - یادآوری مجدد")
                last_reminder = datetime.now()
            
            time.sleep(5)
    
    def cleanup_old_alerts(self, now):
        keys_to_remove = []
        for key in list(self.confirmed_alerts.keys()):
            parts = key.split('-')
            if len(parts) >= 4:
                alert_date = f"{parts[0]}-{parts[1]}-{parts[2]}"
                alert_time = parts[-1]
                alert_datetime = datetime.strptime(f"{alert_date} {alert_time}", "%Y-%m-%d %H:%M")
                
                if now > alert_datetime:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.confirmed_alerts[key]
    
    def start(self):
        print("ربات شروع شد...")
        
        update_thread = threading.Thread(target=self.process_updates, daemon=True)
        update_thread.start()
        
        try:
            self.check_classes()
        except KeyboardInterrupt:
            print("\nربات متوقف شد")
            self.running = False

if __name__ == "__main__":
    bot = ClassReminder()
    bot.start()
