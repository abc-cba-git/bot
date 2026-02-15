import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes


logging.basicConfig(
    format='%(asime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


WEIGHT, HEIGHT, AGE, GENDER, ACTIVITY = range(5)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Рассчитать КБЖУ']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Привет! Я помогу рассчитать твою норму калорий, БЖУ и воды.\n'
        'Нажми кнопку "Рассчитать КБЖУ" чтобы начать.',
        reply_markup=reply_markup
    )



async def calculate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введи свой вес (в кг):')
    return WEIGHT



async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['weight'] = float(update.message.text)
        await update.message.reply_text('Введи свой рост (в см):')
        return HEIGHT
    except ValueError:
        await update.message.reply_text('Пожалуйста, введи число (например: 70)')
        return WEIGHT



async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['height'] = float(update.message.text)
        await update.message.reply_text('Введи свой возраст:')
        return AGE
    except ValueError:
        await update.message.reply_text('Пожалуйста, введи число')
        return HEIGHT



async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['age'] = int(update.message.text)

        keyboard = [['Мужской', 'Женский']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            'Выбери свой пол:',
            reply_markup=reply_markup
        )
        return GENDER
    except ValueError:
        await update.message.reply_text('Пожалуйста, введи возраст числом')
        return AGE



async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text.lower()
    if gender in ['мужской', 'женский']:
        context.user_data['gender'] = gender

        keyboard = [['Низкая', 'Средняя', 'Высокая']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            'Какая у тебя физическая активность?\n'
            'Низкая: сидячая работа, мало движения\n'
            'Средняя: тренировки 3-4 раза в неделю\n'
            'Высокая: физическая работа или спорт каждый день',
            reply_markup=reply_markup
        )
        return ACTIVITY
    else:
        await update.message.reply_text('Пожалуйста, выбери "Мужской" или "Женский"')
        return GENDER



async def calculate_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activity = update.message.text.lower()

    if activity not in ['низкая', 'средняя', 'высокая']:
        await update.message.reply_text('Пожалуйста, выбери уровень активности из кнопок')
        return ACTIVITY


    w = context.user_data['weight']  # вес
    h = context.user_data['height']  # рост
    a = context.user_data['age']  # возраст
    g = context.user_data['gender']  # пол


    if g == 'мужской':
        bmr = (10 * w) + (6.25 * h) - (5 * a) + 5
    else:
        bmr = (10 * w) + (6.25 * h) - (5 * a) - 161


    activity_coef = {
        'низкая': 1.2,
        'средняя': 1.55,
        'высокая': 1.725
    }


    calories = bmr * activity_coef[activity]


    protein = (calories * 0.3) / 4  # 30% от калорий, 4 ккал на грамм
    fat = (calories * 0.25) / 9  # 25% от калорий, 9 ккал на грамм
    carbs = (calories * 0.45) / 4  # 45% от калорий, 4 ккал на грамм


    water = w * 30 / 1000  # в литрах


    result = (
        f"📊 Твоя норма КБЖУ:\n\n"
        f"🔥 Калории: {calories:.0f} ккал\n"
        f"🥩 Белки: {protein:.0f} г\n"
        f"🥑 Жиры: {fat:.0f} г\n"
        f"🍚 Углеводы: {carbs:.0f} г\n\n"
        f"💧 Вода: {water:.1f} л в день\n\n"
        f"Чтобы рассчитать заново, нажми /start"
    )

    await update.message.reply_text(result)


    await update.message.reply_text(
        'Если хочешь пересчитать, нажми /start',
        reply_markup=ReplyKeyboardMarkup([['Рассчитать КБЖУ']], resize_keyboard=True)
    )

    return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Расчёт отменён. Чтобы начать заново, нажми /start',
        reply_markup=ReplyKeyboardMarkup([['Рассчитать КБЖУ']], resize_keyboard=True)
    )
    return ConversationHandler.END


def main():

    TOKEN = "8515729105:AAEfTiciB35lCSi7uj58BDW2PSW40R98Upk"


    application = Application.builder().token(TOKEN).build()


    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text('Рассчитать КБЖУ'), calculate_start)],
        states={
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_result)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)


    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()