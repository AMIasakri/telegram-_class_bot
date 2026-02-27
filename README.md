# 🎓 Telegram Class Reminder Bot

A Telegram bot that automatically sends reminders before your classes start and allows you to confirm your attendance using inline buttons.

This bot is designed to run continuously on a hosting server (such as cPanel Python Setup, VPS, or Linux host).

---

# ✨ Features

* ⏰ Sends reminders before class starts
* 🔁 Sends repeated reminders if not confirmed
* ✅ Attendance confirmation button
* 🔐 Secure configuration using `.env` file
* 🧵 Multi-threaded for smooth performance
* 🖥 Suitable for hosting servers (cPanel, VPS, Linux)

---

# 📁 Project Structure

```
telegram class/
│
├── class_reminder.py   # Main bot script
├── .env                # Environment variables (token, chat id)
└── README.md
```

---

# ⚙️ Requirements

* Python 3.8 or higher
* requests library

Install dependency:

```bash
pip install requests
```

---

# 🔐 Environment Setup

Create a file named `.env` in the same folder:

```
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
```

Example:

```
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
CHAT_ID=123456789
```

---

# ▶️ Run the Bot (Local Test)

Run normally for testing:

```bash
python class_reminder.py
```

If everything is correct, you will see:

```
Bot started...
```

---

# 🌐 Deploy on Host (cPanel Python Setup)

Follow these steps:

---

## 1. Upload Files

Upload these files to your host using File Manager:

```
telegram class/
class_reminder.py
.env
```

Example path:

```
/home/username/telegram class/
```

---

## 2. Open Terminal in cPanel

Go to:

```
cPanel → Terminal
```

---

## 3. Navigate to Project Folder

```bash
cd /home/username/telegram\ class
```

---

## 4. Activate Python Environment

Example:

```bash
source /home/username/virtualenv/telegram\ class/3.11/bin/activate
```

---

## 5. Install requests (if not installed)

```bash
pip install requests
```

---

## 6. Test Run (IMPORTANT)

Run without nohup first:

```bash
python class_reminder.py
```

Check that:

* No errors appear
* Messages are sent correctly

Press:

```
CTRL + C
```

to stop after testing.

---

## 7. Run Permanently (Background Mode)

Run using nohup:

```bash
nohup python class_reminder.py > bot.log 2>&1 &
```

Now the bot will run 24/7 even if you close terminal.

---

# 📄 Check Logs

To view logs:

```bash
tail -f bot.log
```

---

# 🛑 Stop the Bot

Find process:

```bash
ps aux | grep class_reminder.py
```

Kill process:

```bash
kill PID
```

Example:

```bash
kill 12345
```

---

# 🔧 How It Works

The bot:

1. Checks current day and time
2. Compares with class schedule
3. Sends reminder before class
4. Sends repeat reminders if not confirmed
5. Stops reminders after confirmation

---

# 🛡 Security

Sensitive information is stored in `.env` file instead of source code.

Never share your `.env` file publicly.

---

# 👨‍💻 Author

Amir

---

# ⭐ Support

If you like this project, please give it a star ⭐ on GitHub.

