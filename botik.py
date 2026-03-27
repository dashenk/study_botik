import json
import os
import random
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8665004013:AAFCKhlmFVq8djXtrUik6riauHIe1rkmglQ"
TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800",
        caption=(
            "👋 *Привет! Я твой личный бот-мотиватор*\n\n"
            "Помогаю не забывать задачи и двигаться каждый день.\n\n"
            "📋 *Команды:*\n"
            "/add <задача> — добавить задачу\n"
            "/list — все задачи\n"
            "/done <номер> — отметить выполненной\n"
            "/note <номер> <текст> — добавить заметку к задаче\n"
            "/timer <HH:MM> — ежедневное напоминание\n"
            "/motivate — получить мотивацию"
        ),
        parse_mode="Markdown"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_name = " ".join(context.args)
    if not task_name:
        await update.message.reply_text("Напиши задачу после /add\nНапример: /add учить Python")
        return
    tasks = load_tasks()
    tasks.append({"task": task_name, "done": False, "note": ""})
    save_tasks(tasks)
    await update.message.reply_text(f"✅ Добавлено: *{task_name}*", parse_mode="Markdown")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = load_tasks()
    if not tasks:
        await update.message.reply_text("Задач нет. Добавь: /add учить Python")
        return
    text = "*Твои задачи:*\n\n"
    for i, t in enumerate(tasks):
        status = "✅" if t["done"] else "○"
        note = f"\n   📎 _{t['note']}_" if t["note"] else ""
        text += f"{i+1}. {status} {t['task']}{note}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = load_tasks()
    try:
        num = int(context.args[0]) - 1
        tasks[num]["done"] = True
        save_tasks(tasks)
        await update.message.reply_text(
            f"🔥 Выполнено! *{tasks[num]['task']}* — молодец!",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("Используй: /done 1")

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = load_tasks()
    try:
        num = int(context.args[0]) - 1
        text = " ".join(context.args[1:])
        tasks[num]["note"] = text
        save_tasks(tasks)
        await update.message.reply_text("📎 Заметка сохранена!")
    except:
        await update.message.reply_text("Используй: /note 1 твоя заметка")

async def motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [
        "🚀 Ты написала Telegram бота за один день. Большинство людей так и не делают этого.",
        "💡 Каждый эксперт когда-то был там где ты сейчас.",
        "⚡ Экзамены временные. Навыки которые ты строишь — постоянные.",
        "🎯 Одна выполненная задача лучше десяти запланированных.",
        "💪 Сложно сейчас = легко потом. Продолжай.",
        "🌟 Прогресс важнее совершенства. Просто делай."
    ]
    await update.message.reply_text(random.choice(messages))

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time_str = context.args[0]
        hour, minute = map(int, time_str.split(":"))
        chat_id = update.effective_chat.id

        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()

        context.job_queue.run_daily(
            send_daily_reminder,
            time=time(hour=hour, minute=minute),
            chat_id=chat_id,
            name=str(chat_id)
        )

        await update.message.reply_text(
            f"⏰ Готово! Каждый день в *{time_str}* я буду присылать тебе задачи.",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("Используй: /timer 09:00")

async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    tasks = load_tasks()
    pending = [t for t in tasks if not t["done"]]
    if not pending:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="🎉 Все задачи выполнены! Добавь новые: /add"
        )
        return

    quotes = [
        "Маленький шаг сегодня = большой прогресс завтра.",
        "Ты можешь это сделать!",
        "Сегодня хороший день чтобы быть продуктивной."
    ]
    text = "☀️ *Доброе утро! Твои задачи на сегодня:*\n\n"
    for t in pending:
        note = f"\n   📎 _{t['note']}_" if t["note"] else ""
        text += f"○ {t['task']}{note}\n"
    text += f"\n💬 _{random.choice(quotes)}_"

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=text,
        parse_mode="Markdown"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("note", note))
app.add_handler(CommandHandler("motivate", motivate))
app.add_handler(CommandHandler("timer", set_timer))

print("Бот запущен!")
app.run_polling()
