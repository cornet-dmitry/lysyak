import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import os
from dotenv import load_dotenv


load_dotenv()

# Замените на ваш токен
API_TOKEN = os.getenv("BOT_TOKEN")

# Список разрешенных пользователей (их ID)
ALLOWED_USERS = [709913170, 498882491]

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in ALLOWED_USERS:
        await update.message.reply_text('Привет! Я ваш бот для обратной связи.')
    else:
        await update.message.reply_text('У вас нет доступа к этому боту.')


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in ALLOWED_USERS:
        text = update.message.text
        # Здесь можно добавить логику обработки сообщения
        await update.message.reply_text(f'Получено сообщение: {text}')
    else:
        await update.message.reply_text('У вас нет доступа к этому боту.')


# Основная функция
def main():
    # Инициализация бота
    application = Application.builder().token(API_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()