
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# --- Состояния ---
CHOICE, UNITS = range(2)

# --- Ставки для видов работ ---
RATES = {
    'приёмка': 12.76,
    'упаковка': 0  # сюда можно позже добавить реальную ставку

}

# --- Распознавание ввода пользователя ---
CHOICE_MAP = {
    '1': 'приёмка',
    '2': 'упаковка',
    'приемка': 'приёмка',   # без "ё"
    'приёмка': 'приёмка',
    'упаковка': 'упаковка'
}

# --- Старт бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["приёмка", "упаковка"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Выберите тип работы:\n"
        "1 — Приёмка\n2 — Упаковка\n"
        "Можно ввести текстом или цифрой.",
        reply_markup=reply_markup
    )
    return CHOICE

# --- Обработка выбора: приёмка или упаковка ---
async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    choice = CHOICE_MAP.get(text)

    if choice not in RATES:
        await update.message.reply_text(
            "Пожалуйста, выбери один из вариантов:\n"
            "1 — приёмка\n2 — упаковка"
        )
        return CHOICE

    context.user_data['choice'] = choice

    question = {
        'приёмка': "Сколько единиц ты принял(а)?",
        'упаковка': "Сколько единиц ты упаковал(а)?"
    }.get(choice, "Сколько единиц?")

    await update.message.reply_text(question)
    return UNITS

# --- Обработка количества единиц ---
async def units_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    try:
        units = int(text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи целое число.")
        return UNITS

    choice = context.user_data.get('choice')
    rate = RATES.get(choice, 0)

    if units >= 301:
        salary = (units * rate * 1.4 + 3202.5) * 0.87
    else:
        salary = units * rate + 3202.5 * 0.87

    await update.message.reply_text(f"Ваша зарплата за сегодня: {salary:.2f} руб.")
    return ConversationHandler.END

# --- Команда /cancel ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

# --- Запуск приложения ---
import os

TOKEN = os.getenv("BOT_TOKEN")  # Или вставь токен напрямую: TOKEN = "твой_токен_бота"

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice_handler)],
        UNITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, units_handler)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(conv_handler)
app.run_polling()