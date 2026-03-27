import json
import os
import random
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters
)

# 1. БЕЗОПАСНОСТЬ: Берем токен из настроек сервера (Railway)
TOKEN = os.environ.get('BOT_TOKEN')
TASKS_FILE = "tasks.json"

# --- РАБОТА С ФАЙЛАМИ ---
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# --- КОМАНДЫ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с кнопками"""
    # Создаем кнопки (каждый внутренний список [] — это новый ряд кнопок)
    keyboard = [
        [
            InlineKeyboardButton("📋 Мои задачи", callback_data='list'),
            InlineKeyboardButton("🚀 Мотивация", callback_data='motivate')
        ],
        [
            InlineKeyboardButton("➕ Как добавить?", callback_data='add_help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверяем, откуда пришел запрос (сообщение или кнопка)
    target = update.message if update.message else update.callback_query.message

    await target.reply_photo(
        photo="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800",
        caption=(
            "👋 *Привет! Я твой бот-мотиватор*\n\n"
            "Я помогу тебе не забить на учебу и задачи.\n"
            "Используй кнопки ниже или команды из меню."
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление задачи через /add текст"""
    task_name = " ".join(context.args)
    if not task_name:
        await update.message.reply_text("❌ Ошибка! Напиши: `/add учить Python`", parse_mode="Markdown")
        return
    
    tasks = load_tasks()
    tasks.append({"task": task_name, "done": False, "note": ""})
    save_tasks(tasks)
    await update.message.reply_text(f"✅ Добавлено: *{task_name}*", parse_mode="Markdown")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод списка задач (работает и из кнопок, и через /list)"""
    # Если вызвано кнопкой, нужно ответить на callback_query
    query = update.callback_query
    if query:
        await query.answer()
        target = query.message
    else:
        target = update.message

    tasks = load_tasks()
    if not tasks:
        await target.reply_text("Задач пока нет. Добавь первую через /add!")
        return

    text = "*Твои задачи:*\n\n"
    for i, t in enumerate(tasks):
        status = "✅" if t["done"] else "○"
        text += f"{i+1}. {status} {t['task']}\n"
    
    await target.reply_text(text, parse_mode="Markdown")

async def motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рандомная цитата"""
    query = update.callback_query
    if query: await query.answer()
    
    messages = [
        "🚀 Ты создала этого бота сама! Это уже круче, чем у 90% людей.",
        "💡 Маленькие шаги ведут к большим результатам.",
        "⚡ Ошибки в коде — это просто опыт, а не провал.",
        "🎯 Сфокусируйся на одной задаче и доведи её до конца."
    ]
    target = update.message if update.message else update.callback_query.message
    await target.reply_text(random.choice(messages))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    data = query.data

    if data == 'list':
        await list_tasks(update, context)
    elif data == 'motivate':
        await motivate(update, context)
    elif data == 'add_help':
        await query.answer()
        await query.message.reply_text("Просто напиши в чат: `/add Название задачи`", parse_mode="Markdown")

# --- ЗАПУСК БОТА ---

if __name__ == '__main__':
    # Проверка, что токен вообще есть
    if not TOKEN:
        print("ОШИБКА: Токен не найден в переменных окружения!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()

        # Регистрация команд
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("add", add))
        app.add_handler(CommandHandler("list", list_tasks))
        app.add_handler(CommandHandler("motivate", motivate))
        
        # Регистрация кнопок
        app.add_handler(CallbackQueryHandler(handle_callback))

        print("🚀 Бот запущен и готов к работе!")
        app.run_polling()