from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import logging

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOOSING_DIRECTION, CHOOSING_SECTION = range(2)

# Полное расписание с направлениями, разделами и программами
schedule = {
    "Наука": {
        "Естественно-научные программы": [
            {"День": "Понедельник", "Время": "16:00 – 18:30", "Программа": "Биология для знатоков. 9 класс", "Преподаватель": "Майорова Антонина Дмитриевна", "Кабинет": "Агробиотехнологии"},
            {"День": "Понедельник", "Время": "16:00 – 18:30", "Программа": "Биология с основами генетики", "Преподаватель": "Агапова Ирина Борисовна", "Кабинет": "Биология и генетика"},
            {"День": "Понедельник", "Время": "16:30 – 19:00", "Программа": "Биохимия", "Преподаватель": "Гришина Ольга Владимировна", "Кабинет": "Химия"},
            {"День": "Вторник", "Время": "15:30-18:00", "Программа": "Агробиотехнологии. Нескучная наука", "Преподаватель": "Микаелян Регина Гарегиновна", "Кабинет": "Агробиотехнологии"},
            {"День": "Вторник", "Время": "17:00-20:00", "Программа": "В лабиринтах химии, 5-6 класс", "Преподаватель": "Бубнова Ксения Евгеньевна", "Кабинет": "Химия"},
            {"День": "Вторник", "Время": "15:30 – 18.30", "Программа": "Экомир", "Преподаватель": "Гусева Анна Юрьевна", "Кабинет": "Биология и генетика"},
            {"День": "Среда", "Время": "16:00 – 18:30", "Программа": "Тайны происхождения", "Преподаватель": "Закатова Ирина Александровна", "Кабинет": "Биология и генетика"},
            {"День": "Среда", "Время": "16:00 – 18:30", "Программа": "Биология для знатоков. 10 класс", "Преподаватель": "Майорова Антонина Дмитриевна", "Кабинет": "Физика и альтернативная энергетика"},
            {"День": "Среда", "Время": "14:30-17:00", "Программа": "Проектная деятельность по химии", "Преподаватель": "Кузнецов Владимир Васильевич", "Кабинет": "Химия"},
            {"День": "Среда", "Время": "17:00-20:00", "Программа": "Проектный тренинг по химии и нанотехнологиям", "Преподаватель": "Торшинина Надежда Александровна", "Кабинет": "Химия"},
            {"День": "Четверг", "Время": "16:30-18:00", "Программа": "Биологическая школа «Биосфера»", "Преподаватель": "Закатова Ирина Александровна", "Кабинет": "Биология и генетика"},
            {"День": "Четверг", "Время": "16:00-19:00", "Программа": "В лабиринтах химии 7-8 класс", "Преподаватель": "Бубнова Ксения Евгеньевна", "Кабинет": "Химия"},
            {"День": "Четверг", "Время": "15:30 – 18:30", "Программа": "Основы экологии. Методика экологических исследований", "Преподаватель": "Гусева Анна Юрьевна", "Кабинет": "Биология и генетика"},
            {"День": "Пятница", "Время": "15:30 – 18:00", "Программа": "Агробиотехнологии. Нескучная наука", "Преподаватель": "Микаелян Регина Гарегиновна", "Кабинет": "Агробиотехнологии"},
            {"День": "Пятница", "Время": "17:00-20:00", "Программа": "Проектный тренинг по химии и нанотехнологиям", "Преподаватель": "Торшинина Надежда Александровна", "Кабинет": "Химия"},
            {"День": "Пятница", "Время": "17:00 – 20:00", "Программа": "Математика 7.0", "Преподаватель": "Токарев Сергей Иванович", "Кабинет": "Малый зал"},
            {"День": "Пятница", "Время": "15:30 – 18.30", "Программа": "Экомир", "Преподаватель": "Гусева Анна Юрьевна", "Кабинет": "Биология и генетика"},
            {"День": "Суббота", "Время": "10:00 – 12:30", "Программа": "Основы экологии. Методика экологических исследований (Группа 1)", "Преподаватель": "Гусева Анна Юрьевна", "Кабинет": "Биология и генетика"},
            {"День": "Суббота", "Время": "10:00-13:00", "Программа": "Олимпиадная химия для старшеклассников", "Преподаватель": "Кузнецов Владимир Васильевич", "Кабинет": "Химия"},
            {"День": "Суббота", "Время": "13:00 – 15:30", "Программа": "Химия. Старт в науку. 1 группа", "Преподаватель": "Буймова Светлана Александровна", "Кабинет": "Химия"},
            {"День": "Суббота", "Время": "15:30 – 18.30", "Программа": "Химия. Старт в науку. 2 группа", "Преподаватель": "Буймова Светлана Александровна", "Кабинет": "Химия"},
            {"День": "Воскресенье", "Время": "11:00 – 13:30", "Программа": "Математика 7.0", "Преподаватель": "Токарев Сергей Иванович", "Кабинет": "405"},
        ],
        "Технические программы": [
            {"День": "Понедельник", "Время": "16:00 – 18:30", "Программа": "Основы 3D-моделирования. Продвинутый уровень", "Преподаватель": "Миронов Евгений Викторович", "Кабинет": "Математика и информатика"},
            {"День": "Понедельник", "Время": "16:00 – 18:30", "Программа": "Математическая мозаика", "Преподаватель": "Крупина Светлана Сергеевна", "Кабинет": "Физика и альтернативная энергетика"},
            {"День": "Вторник", "Время": "16:00 – 18:30", "Программа": "Информатика. Юниоры. Программирование на Python", "Преподаватель": "Фокин Станислав Антонович", "Кабинет": "Математика и информатика"},
            {"День": "Среда", "Время": "16:00 – 18:30", "Программа": "Информатика. Программирование на Python. Продвинутый уровень", "Преподаватель": "Фокин Станислав Антонович", "Кабинет": "Математика и информатика"},
            {"День": "Четверг", "Время": "16:00 – 18:30", "Программа": "Искусственный интеллект и машинное обучение", "Преподаватель": "Фокин Станислав Антонович", "Кабинет": "Математика и информатика"},
            {"День": "Четверг", "Время": "15:30 – 18:00", "Программа": "Основы графического дизайна", "Преподаватель": "Захарова Нина Валентиновна", "Кабинет": "Графика и промышленный дизайн"},
            {"День": "Четверг", "Время": "16:00 – 18:30", "Программа": "Основы робототехники и программирование роботов. 6-7 класс", "Преподаватель": "Захаров Михаил Алексеевич", "Кабинет": "Физика и альтернативная энергетика"},
            {"День": "Пятница", "Время": "15:30 – 18:00", "Программа": "Основы графического дизайна", "Преподаватель": "Захарова Нина Валентиновна", "Кабинет": "Графика и промышленный дизайн"},
            {"День": "Пятница", "Время": "17:00 – 20:00", "Программа": "Математика 7.0", "Преподаватель": "Токарев Сергей Иванович", "Кабинет": "Малый зал"},
            {"День": "Пятница", "Время": "16:00 – 18:30", "Программа": "Основы 3D-моделирования", "Преподаватель": "Миронов Евгений Викторович", "Кабинет": "Математика и информатика"},
            {"День": "Пятница", "Время": "16:30 – 19:00", "Программа": "Современная энергетика", "Преподаватель": "Лихачева Анна Валентиновна", "Кабинет": "Физика и альтернативная энергетика"},
            {"День": "Суббота", "Время": "10:00 – 12:30", "Программа": "Информатика. Юниоры. Программирование на Python", "Преподаватель": "Бегунов Дмитрий Игоревич", "Кабинет": "Математика и информатика"},
            {"День": "Суббота", "Время": "9:00 – 11:30", "Программа": "Основы графического дизайна. Продвинутый уровень", "Преподаватель": "Захарова Нина Валентиновна", "Кабинет": "Графика и промышленный дизайн"},
            {"День": "Суббота", "Время": "15:00 – 17:30", "Программа": "Основы робототехники и программирование роботов", "Преподаватель": "Захаров Михаил Алексеевич", "Кабинет": "Физика и альтернативная энергетика"},
        ],
        "Гуманитарные программы": [
            {"День": "Среда", "Время": "16:30 – 19:00", "Программа": "Итальянский язык", "Преподаватель": "Усачева Татьяна Рудольфовна", "Кабинет": "Агробиотехнологии"},
            {"День": "Суббота", "Время": "10:00 – 12:30", "Программа": "«Во глубине словесных руд»", "Преподаватель": "Парфенова Елена Львовна", "Кабинет": "Физика и альтернативная энергия"},
            {"День": "Суббота", "Время": "11:00 – 13:30", "Программа": "Олимпиадная история", "Преподаватель": "Ерискина Елена Дмитриевна", "Кабинет": "Биология и генетика"},
        ],
        "Дистанционные программы": [
            {"День": "Вторник", "Время": "18:00 – 20:30", "Программа": "Онлайн-школа по информатике «Вектор37»", "Преподаватель": "Сидоров Михаил Владимирович", "Кабинет": "Дистанционно"},
            {"День": "Среда", "Время": "18:00 – 20:30", "Программа": "Дистанционный тренинг по физике 10 класс", "Преподаватель": "Крючкова Галина Георгиевна", "Кабинет": "Дистанционно"},
            {"День": "Четверг", "Время": "18:30 – 20:30", "Программа": "Онлайн-школа по математике «Вектор37»", "Преподаватель": "Власов Евгений Викторович", "Кабинет": "Дистанционно"},
            {"День": "Суббота", "Время": "10:00 – 12:00 (2 раза в месяц по 2 часа)", "Программа": "Тропою исследований", "Преподаватель": "Агапов Андрей Викторович", "Кабинет": "Дистанционно"},
        ],
    },
    "Искусство": {
        "Цирковое искусство": [
            {"День": "Понедельник", "Время": "16:00 - 18:00", "Программа": "Цирковая студия «Арлекино» 1, 2 группа", "Преподаватель": "Привалова Наталья Владимировна", "Кабинет": "Спортивный зал"},
            {"День": "Среда", "Время": "16:00 - 18:00", "Программа": "Цирковая студия «Арлекино» 1, 2 группа", "Преподаватель": "Привалова Наталья Владимировна", "Кабинет": "Спортивный зал"},
            {"День": "Пятница", "Время": "16:00 - 18:00", "Программа": "Цирковая студия «Арлекино» 1, 2 группа", "Преподаватель": "Привалова Наталья Владимировна", "Кабинет": "Спортивный зал"},
            {"День": "Воскресенье", "Время": "12:00 - 14:00", "Программа": "Цирковая студия «Арлекино» 1, 2 группа", "Преподаватель": "Привалова Наталья Владимировна", "Кабинет": "Спортивный зал"},
        ],
        "Вокал": [
            {"День": "Понедельник", "Время": "18:00 - 20:30", "Программа": "ЭА «Неразлучные друзья» основной состав", "Преподаватель": "Соковы Марина Альбертовна, Наталья Альбертовна", "Кабинет": "Вокальная студия"},
            {"День": "Вторник", "Время": "16:00 - 18:00", "Программа": "ЭА «Неразлучные друзья» основной состав", "Преподаватель": "Соковы Марина Альбертовна, Наталья Альбертовна", "Кабинет": "Вокальная студия"},
            {"День": "Среда", "Время": "16:00 - 18:00", "Программа": "ЭА «Неразлучные друзья» основной состав", "Преподаватель": "Соковы Марина Альбертовна, Наталья Альбертовна", "Кабинет": "Вокальная студия"},
            {"День": "Четверг", "Время": "18:00 - 20:30", "Программа": "ЭА «Неразлучные друзья» основной состав", "Преподаватель": "Соковы Марина Альбертовна, Наталья Альбертовна", "Кабинет": "Вокальная студия"},
            {"День": "Пятница", "Время": "16:00 - 18:00", "Программа": "ЭА «Неразлучные друзья» основной состав", "Преподаватель": "Соковы Марина Альбертовна, Наталья Альбертовна", "Кабинет": "Вокальная студия"},
        ],
        "Танцы": [
            {"День": "Понедельник", "Время": "17:00 - 17:45", "Программа": "В такт с музыкой (бальные танцы, младшая гр)", "Преподаватель": "Слесаренко Наталья Ивановна", "Кабинет": "Белый зал"},
            {"День": "Понедельник", "Время": "18:30 - 20:00", "Программа": "В такт с музыкой (бальные танцы, младшая гр)", "Преподаватель": "Слесаренко Наталья Ивановна", "Кабинет": "Белый зал"},
            {"День": "Вторник", "Время": "17:00 - 20:00", "Программа": "Основы классического танца (балет) 1г.о.", "Преподаватель": "Нечаева Юлия Вячеславовна", "Кабинет": "Белый зал"},
            {"День": "Вторник", "Время": "17:00 - 18:00", "Программа": "В такт с музыкой (бальные танцы, основная гр)", "Преподаватель": "Слесаренко Игорь Борисович", "Кабинет": "Белый зал"},
            {"День": "Среда", "Время": "17:00 - 17:45", "Программа": "В такт с музыкой (бальные танцы, младшая гр)", "Преподаватель": "Слесаренко Наталья Ивановна", "Кабинет": "Белый зал"},
            {"День": "Среда", "Время": "18:30 - 20:00", "Программа": "В такт с музыкой (бальные танцы, младшая гр)", "Преподаватель": "Слесаренко Наталья Ивановна", "Кабинет": "Белый зал"},
            {"День": "Четверг", "Время": "17:00 - 18:00", "Программа": "В такт с музыкой (бальные танцы, основная гр)", "Преподаватель": "Слесаренко Игорь Борисович", "Кабинет": "Белый зал"},
            {"День": "Четверг", "Время": "18:00 - 20:00", "Программа": "В такт с музыкой (бальные танцы, основная гр)", "Преподаватель": "Слесаренко Игорь Борисович", "Кабинет": "Белый зал"},
            {"День": "Суббота", "Время": "18:00 - 20:00", "Программа": "В такт с музыкой (бальные танцы, основная гр)", "Преподаватель": "Слесаренко Игорь Борисович", "Кабинет": "Белый зал"},
        ],
        "Художественное искусство": [
            {"День": "Вторник", "Время": "14:00 - 16:45", "Программа": "Основы классического рисунка и живописи", "Преподаватель": "Черепенина Юлия Вячеславовна", "Кабинет": "Студия живописи"},
            {"День": "Среда", "Время": "14:30 - 16:30", "Программа": "Основы классического рисунка и живописи", "Преподаватель": "Черепенина Юлия Вячеславовна", "Кабинет": "Студия живописи"},
            {"День": "Четверг", "Время": "15:00 - 17:00", "Программа": "Студия ювелирного дизайна «Грани»", "Преподаватель": "Бессонова Ксения Евгеньевна", "Кабинет": "Ювелирный дизайн"},
            {"День": "Четверг", "Время": "17:00 - 19:00", "Программа": "Студия ювелирного дизайна «Грани»", "Преподаватель": "Бессонова Ксения Евгеньевна", "Кабинет": "Ювелирный дизайн"},
            {"День": "Пятница", "Время": "15:30 - 17:30", "Программа": "Юные дизайнеры одежды 1 группа", "Преподаватель": "Кузина Юлия Андреевна", "Кабинет": "Студия моды и дизайна"},
            {"День": "Суббота", "Время": "11:00 - 13:30", "Программа": "Юные дизайнеры одежды 1 группа", "Преподаватель": "Кузина Юлия Андреевна", "Кабинет": "Студия моды и дизайна"},
        ],
    },
    "Спорт": {
        "Шахматы": [
            {"День": "Суббота", "Время": "14:00-16:00", "Программа": "Шахматы. Совершенствование мастерства", "Преподаватель": "Рыбкин Михаил Сергеевич", "Кабинет": "Малый зал"},
            {"День": "Суббота", "Время": "16:00-18:00", "Программа": "Шахматы. Совершенствование мастерства", "Преподаватель": "Рыбкин Михаил Сергеевич", "Кабинет": "Малый зал"},
            {"День": "Суббота", "Время": "18:00-20:00", "Программа": "Шахматы. Совершенствование мастерства", "Преподаватель": "Рыбкин Михаил Сергеевич", "Кабинет": "Малый зал"},
        ],
    },
}

# Команда /start
async def start(update: Update, context: CallbackContext) -> int:
    buttons = [["Наука", "Искусство", "Спорт"]]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    await update.message.reply_text("Выберите направление:", reply_markup=reply_markup)
    return CHOOSING_DIRECTION

# Обработка выбора направления
async def choose_direction(update: Update, context: CallbackContext) -> int:
    direction = update.message.text
    if direction in schedule:
        context.user_data["direction"] = direction  # Сохраняем выбранное направление
        sections = list(schedule[direction].keys())
        buttons = [[section] for section in sections]
        buttons.append(["Назад"])  # Добавляем кнопку "Назад"
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
        await update.message.reply_text(f"Выберите раздел для направления {direction}:", reply_markup=reply_markup)
        return CHOOSING_SECTION
    else:
        await update.message.reply_text("Пожалуйста, выберите направление из списка.")
        return CHOOSING_DIRECTION

# Обработка выбора раздела
async def choose_section(update: Update, context: CallbackContext) -> int:
    section = update.message.text
    if section == "Назад":  # Обработка кнопки "Назад"
        return await start(update, context)
    else:
        direction = context.user_data.get("direction")
        if direction and section in schedule[direction]:
            programs = schedule[direction][section]
            response = f"Расписание для раздела «{section}»:\n\n"
            for program in programs:
                response += (
                    f"День: {program['День']}\n"
                    f"Время: {program['Время']}\n"
                    f"Программа: {program['Программа']}\n"
                    f"Преподаватель: {program['Преподаватель']}\n"
                    f"Кабинет: {program['Кабинет']}\n\n"
                )
            await update.message.reply_text(response)
            return CHOOSING_SECTION
        else:
            await update.message.reply_text("Пожалуйста, выберите раздел из списка.")
            return CHOOSING_SECTION

# Завершение диалога
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("До свидания!")
    return ConversationHandler.END

def main() -> None:
    # Вставьте сюда ваш токен
    application = Application.builder().token("7977475343:AAE9kcchf0GxmQMqzh37XZDgqlCKntckNmA").build()

    # ConversationHandler для управления состояниями
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_DIRECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_direction)
            ],
            CHOOSING_SECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_section)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
