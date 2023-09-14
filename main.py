import telebot, sqlite3, requests, random
from telebot import types
from datetime import datetime, timedelta
from texts import financial_advice

TOKEN = '5849575828:AAGdAbpIoPGmkM-TWMAcQ8guq8nvcv0PoHM'
bot = telebot.TeleBot(TOKEN)

# Главное меню
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
items = [
    "Доходы ⬆️",
    "Расходы ⬇️",
    "Учет 〽️",
    "Советник 🧙‍♂️",
    "Инфо ℹ️",
]
main_menu.add(*items)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = (
        f"Привет, {message.from_user.first_name}! 🕺\n"
        "Давайте же возьмем финансы под контроль\n"
        '\n'
        "Выберите категорию:"
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=main_menu)


# Обработчик кнопки "Доходы"
@bot.message_handler(func=lambda message: message.text == "Доходы ⬆️")
def handle_income(message):
    bot.send_message(message.chat.id, "Меню доходов:", reply_markup=income_menu)


# Меню доходов
income_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
item_add_income = types.KeyboardButton("Добавить доход")
item_undo_income = types.KeyboardButton("Отменить последний доход")
item_list_income = types.KeyboardButton("Список доходов")
item_back = types.KeyboardButton("Вернуться в главное меню")
income_menu.add(item_add_income, item_undo_income, item_list_income, item_back)


# Создаем базу данных и таблицу "income" с датой (месяц и год) при запуске бота
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        date TEXT
    )
''')
conn.commit()
conn.close()


# Обработчик кнопки "Доход"
@bot.message_handler(func=lambda message: message.text == "Добавить доход")
def add_income(message):
    msg = bot.send_message(message.chat.id, "Введите сумму дохода:")
    bot.register_next_step_handler(msg, save_income)


def save_income(message):
    try:
        income_amount = int(message.text)  # Получаем сумму дохода от пользователя
        current_date = datetime.now().strftime('%Y.%m.%d')  # Получаем текущую дату

        # Вставляем данные о доходе в базу данных с текущей датой
        add_income_to_db(income_amount, current_date)

        bot.send_message(message.chat.id, f"Доход в размере {income_amount} успешно добавлен!")

        # После успешного добавления дохода, вызываем обработчик кнопки "Доходы" для отображения меню доходов
        handle_income(message)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат суммы дохода. Введите сумму числом.")


def add_income_to_db(amount, date):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (amount, date) VALUES (?, ?)", (amount, date))
    conn.commit()
    conn.close()


# Обработчик кнопки "Отменить последний доход"
@bot.message_handler(func=lambda message: message.text == "Отменить последний доход")
def undo_last_income(message):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Выбираем ID последней записи о доходе
    cursor.execute("SELECT id FROM income ORDER BY id DESC LIMIT 1")
    last_income_id = cursor.fetchone()

    if last_income_id:
        last_income_id = last_income_id[0]
        # Удаляем последнюю запись о доходе
        cursor.execute("DELETE FROM income WHERE id=?", (last_income_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Последний доход успешно отменен.")
    else:
        bot.send_message(message.chat.id, "Список доходов пуст.")

    conn.close()


# Обработчик кнопки "Список доходов"
@bot.message_handler(func=lambda message: message.text == "Список доходов")
def list_income(message):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, date FROM income")
    income_records = cursor.fetchall()
    conn.close()

    if income_records:
        income_list = ""
        total_income = 0

        for record in income_records:
            income_id, income_amount, income_date = record
            income_list += f"{income_id}) {income_date} ➖ {int(income_amount)} сом\n"
            total_income += int(income_amount)

        bot.send_message(message.chat.id, f"Список доходов:\n{income_list}\nОбщая сумма доходов: {total_income} сом")
    else:
        bot.send_message(message.chat.id, "Список доходов пуст.")


# Обработчик кнопки "Расходы"
@bot.message_handler(func=lambda message: message.text == "Расходы ⬇️")
def handle_expenses(message):
    bot.send_message(message.chat.id, "Меню расходов:", reply_markup=expenses_menu)


# Меню расходов
expenses_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
item_add_expense = types.KeyboardButton("Добавить расход")
item_undo_expense = types.KeyboardButton("Отменить последний расход")
item_list_expense = types.KeyboardButton("Список расходов")
item_back = types.KeyboardButton("Вернуться в главное меню")
expenses_menu.add(item_add_expense, item_undo_expense, item_list_expense, item_back)


# Создаем базу данных и таблицу "expenses" с датой (месяц и год) при запуске бота
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        date TEXT
    )
''')
conn.commit()
conn.close()


# Обработчик кнопки "Добавить расход"
@bot.message_handler(func=lambda message: message.text == "Добавить расход")
def add_expense(message):
    msg = bot.send_message(message.chat.id, "Введите сумму расхода:")
    bot.register_next_step_handler(msg, save_expense)


def save_expense(message):
    try:
        expense_amount = int(message.text)  # Получаем сумму расхода от пользователя
        current_date = datetime.now().strftime('%Y.%m.%d')  # Получаем текущую дату

        # Вставляем данные о расходе в базу данных с текущей датой
        add_expense_to_db(expense_amount, current_date)

        bot.send_message(message.chat.id, f"Расход в размере {expense_amount} успешно добавлен!")

        # После успешного добавления расхода, вызываем обработчик кнопки "Расходы" для отображения меню расходов
        handle_expenses(message)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат суммы расхода. Введите сумму числом.")


def add_expense_to_db(amount, date):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, date) VALUES (?, ?)", (amount, date))
    conn.commit()
    conn.close()


# Обработчик кнопки "Отменить последний расход"
@bot.message_handler(func=lambda message: message.text == "Отменить последний расход")
def undo_last_expense(message):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Выбираем ID последней записи о расходе
    cursor.execute("SELECT id FROM expenses ORDER BY id DESC LIMIT 1")
    last_expense_id = cursor.fetchone()

    if last_expense_id:
        last_expense_id = last_expense_id[0]
        # Удаляем последнюю запись о расходе
        cursor.execute("DELETE FROM expenses WHERE id=?", (last_expense_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Последний расход успешно отменен.")
    else:
        bot.send_message(message.chat.id, "Список расходов пуст.")

    conn.close()


# Обработчик кнопки "Список расходов"
@bot.message_handler(func=lambda message: message.text == "Список расходов")
def list_expenses(message):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, date FROM expenses")
    expense_records = cursor.fetchall()
    conn.close()

    if expense_records:
        expense_list = ""
        total_expenses = 0

        for record in expense_records:
            expense_id, expense_amount, expense_date = record
            expense_list += f"{expense_id}) {expense_date} ➖ {int(expense_amount)} сом\n"
            total_expenses += int(expense_amount)

        bot.send_message(message.chat.id,
                         f"Список расходов:\n{expense_list}\nОбщая сумма расходов: {total_expenses} сом")
    else:
        bot.send_message(message.chat.id, "Список расходов пуст.")


# Обработчик кнопки "Статистика"
@bot.message_handler(func=lambda message: message.text == "Учет 〽️")
def statistics(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Создаем кнопки для разных периодов
    month_button = types.KeyboardButton("За месяц")
    three_months_button = types.KeyboardButton("За три месяца")
    half_year_button = types.KeyboardButton("Полгода")
    year_button = types.KeyboardButton("Год")
    back_to_main_menu_button = types.KeyboardButton("Вернуться в главное меню")

    markup.add(month_button, three_months_button)
    markup.add(half_year_button, year_button)
    markup.add(back_to_main_menu_button)

    bot.send_message(message.chat.id, "Выберите период статистики:", reply_markup=markup)


# Функция для получения статистики за заданный период
def get_statistics_for_period(period_days):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    cursor.execute("SELECT SUM(amount) FROM income WHERE date BETWEEN ? AND ?",
                   (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y.%m.%d')))
    total_income = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                   (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y.%m.%d')))
    total_expenses = cursor.fetchone()[0]

    total_income = int(total_income) if total_income else 0
    total_expenses = int(total_expenses) if total_expenses else 0

    conn.close()

    return total_income, total_expenses


# Функция для получения начальной и конечной даты для периода
def get_period_dates(period_days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    return start_date, end_date


# Обработчики кнопок для статистики за разные периоды
def handle_period_statistics(message, period_days):
    total_income, total_expenses = get_statistics_for_period(period_days)
    start_date, end_date = get_period_dates(period_days)

    # Получите текстовое представление начальной и конечной даты в формате "число месяца"
    start_date_str = start_date.strftime('%d.%m')
    end_date_str = end_date.strftime('%d.%m')

    if period_days == 30:
        period_name = f"Статистика за месяц ({start_date_str} - {end_date_str}):"
    elif period_days == 90:
        period_name = f"Статистика за три месяца ({start_date_str} - {end_date_str}):"
    elif period_days == 180:
        period_name = f"Статистика за полгода ({start_date_str} - {end_date_str}):"
    elif period_days == 365:
        period_name = f"Статистика за год ({start_date_str} - {end_date_str}):"
    else:
        period_name = "Неизвестный период"

    response_text = f"{period_name}\n\n"
    response_text += f"Общий доход🔺: {total_income} сом\n"
    response_text += f"Общий расход🔻: {total_expenses} сом"

    bot.send_message(message.chat.id, response_text)


@bot.message_handler(func=lambda message: message.text == "За месяц")
def stats_for_month(message):
    handle_period_statistics(message, 30)


@bot.message_handler(func=lambda message: message.text == "За три месяца")
def stats_for_three_months(message):
    handle_period_statistics(message, 90)


@bot.message_handler(func=lambda message: message.text == "Полгода")
def stats_for_half_year(message):
    handle_period_statistics(message, 180)


@bot.message_handler(func=lambda message: message.text == "Год")
def stats_for_year(message):
    handle_period_statistics(message, 365)


# Обработчик кнопки "Советник"
@bot.message_handler(func=lambda message: message.text == "Советник 🧙‍♂️")
def start_shopper_advice(message):
    bot.send_message(message.chat.id, "Ваш личный советник, чтобы уберечь ваши финансы.\n Ответьте на вопросы ниже:")
    ask_question(message.chat.id, 0, 0, 0)


questions = [
    "1.Вы действительно нуждаетесь в этом товаре?",
    "2.Вы уже искали альтернативы или сравнили цены?",
    "3.У меня есть финансовая возможность сейчас приобрести это без вреда для бюджета?",
    "4.Можете ли вы подождать и подумать некоторое время перед покупкой?",
    "5.Это покупка запланирована? ",
    "6.Могу ли я найти альтернативное решение, которое будет стоить меньше или не потребует затрат?",
    "7.Это приоритет среди других целей и расходов, которые у меня есть?",
    "8.Соответствует покупка вашими текущими целям и приоритетам?",
    "9.Сможете ли вы отложить деньги на эту покупку, чтобы избежать кредита?",
]


def ask_question(chat_id, question_index, yes_count, no_count):
    if question_index < len(questions):
        question = questions[question_index]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Да", "Нет", "/cancel")  # Добавляем кнопку /cancel
        bot.send_message(chat_id, question, reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: process_answer(message, question_index, yes_count, no_count))
    else:
        # Завершаем клавиатуру и добавляем только кнопку "В главное меню"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Вернуться в главное меню")
        bot.send_message(chat_id, "Оценка результата...", reply_markup=markup)
        if yes_count > no_count:
            bot.send_message(chat_id, "Совет: Вы можете сделать эту покупку.")
        else:
            bot.send_message(chat_id, "Совет: Подумайте ещё, покупка похожа на импульсивную.")


def process_answer(message, question_index, yes_count, no_count):
    answer = message.text.lower()
    if answer == "да":
        yes_count += 1
    elif answer == "нет":
        no_count += 1
    elif answer == "/cancel":  # Обработка команды /cancel
        bot.send_message(message.chat.id, "Опрос прерван.")
        # Возвращаем пользователя в главное меню
        handle_back(message)
        return

    # Переходим к следующему вопросу
    question_index += 1
    ask_question(message.chat.id, question_index, yes_count, no_count)


# Обработчик кнопки "Инфо"
@bot.message_handler(func=lambda message: message.text == "Инфо ℹ️")
def info_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    info_items = ["Статус финансов", "Курсы валют", "Вернуться в главное меню"]
    markup.add(*info_items)
    bot.send_message(message.chat.id, "Меню Инфо:", reply_markup=markup)


# Обработчик кнопки "Статус финансов"
@bot.message_handler(func=lambda message: message.text == "Статус финансов")
def financial_status(message):
    # функция для вычисления процента превышения доходов над расходами или наоборот
    def calculate_income_expense_ratio():
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM income")
        total_income = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = cursor.fetchone()[0]
        conn.close()

        if total_income is None:
            total_income = 0
        if total_expenses is None:
            total_expenses = 0

        if total_income >= total_expenses:
            income_expense_ratio = (total_income - total_expenses) / total_income * 100
            return income_expense_ratio
        else:
            income_expense_ratio = (total_expenses - total_income) / total_expenses * 100
            return -income_expense_ratio
    ratio = calculate_income_expense_ratio()

    if ratio >= 100:
        bot.send_message(message.chat.id, "Доходы больше расходов на 100%. Отлично управляетесь с финансами!")
    elif ratio >= 75:
        bot.send_message(message.chat.id, "Доходы больше расходов на 75%. Финансово стабильная ситуация!")
    elif ratio >= 50:
        bot.send_message(message.chat.id, "Доходы больше расходов на 50%. Это хороший результат!")
    elif ratio >= 25:
        bot.send_message(message.chat.id, "Доходы больше расходов на 25%. Продолжайте в том же духе!")
    elif ratio >= -25:
        bot.send_message(message.chat.id, "Расходы больше доходов на 25%. Обратите внимание на управление расходами.")
    elif ratio >= -50:
        bot.send_message(message.chat.id, "Расходы больше доходов на 50%. Пересмотрите свои финансовые планы.")
    elif ratio >= -75:
        bot.send_message(message.chat.id, "Расходы больше доходов на 75%. Ситуация требует внимания и коррекции.")
    else:
        bot.send_message(message.chat.id, "Расходы больше доходов на 100%. Срочно примите меры по фин. стабилизации.")

    # Выбираем случайный финансовый совет
    random_advice = random.choice(financial_advice)
    bot.send_message(message.chat.id, f"Финансовый совет дня: \n{random_advice}")


# Обработчик кнопки "Курсы валют"
@bot.message_handler(func=lambda message: message.text == "Курсы валют")
def currency_rates(message):
    # Получите данные о курсах валют с сайта
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    data = response.json()

    # Извлеките нужные данные о курсах валют
    usd_rate = data["Valute"]["USD"]["Value"] * 0.925
    eur_rate = data["Valute"]["EUR"]["Value"] * 0.925
    kzt_rate = data["Valute"]["KZT"]["Value"] * 0.925
    cny_rate = data["Valute"]["CNY"]["Value"] * 0.925
    jpy_rate = data["Valute"]["JPY"]["Value"] * 0.925

    # Отправьте сообщение с курсами валют с точностью до одной десятой
    currency_message = f"Курсы валют:\n\n" \
                       f"Доллар $ - {usd_rate:.1f} сом\n" \
                       f"Евро € - {eur_rate:.1f} сом\n" \
                       f"Тенге ₸ - {kzt_rate:.1f} сом\n" \
                       f"Юань ￥ - {cny_rate:.1f} сом\n" \
                       f"Иена ¥ - {jpy_rate:.1f} сом\n" \

    bot.send_message(message.chat.id, currency_message)


@bot.message_handler(func=lambda message: message.text == "Вернуться в главное меню")
def return_to_main_menu_from_info(message):
    bot.send_message(message.chat.id, "Вы вернулись в главное меню.", reply_markup=main_menu)


# Обработчик кнопки "Вернуться в главное меню"
@bot.message_handler(func=lambda message: message.text == "Вернуться в главное меню")
def handle_back(message):
    bot.send_message(message.chat.id, "Возвращаемся в главное меню.", reply_markup=main_menu)


# Обработчик для текстовых сообщений, которые не соответствуют меню
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Проверяем, содержит ли сообщение текст
    if message.text:
        bot.send_message(message.chat.id, "Пожалуйста, выберите категорию или пункт меню.")
    else:
        bot.send_message(message.chat.id, "Получено сообщение без текста.")


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
