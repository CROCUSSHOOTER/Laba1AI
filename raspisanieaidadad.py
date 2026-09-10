import os
import json
import datetime
import zoneinfo
import pandas as pd
from telebot import TeleBot, types

# Конфигурация бота
TOKEN = "8939964187:AAFf2Ef00fO2Lze53ijAMIxSnY_YVhNpHXQ"
EXCEL_FILE = "2 курс ФИиИТ ФИиИС Расписание 1 академического периода 2026-2027уч.года.xlsx"

bot = TeleBot(TOKEN)

# ----------------------------------------------------------------------
# 1. Функция автоматического парсинга Excel
# ----------------------------------------------------------------------
def parse_excel_schedule(file_path):
    """Считывает Excel-файл и формирует словарик с расписанием ТИИ-25-21"""
    if not os.path.exists(file_path):
        print(f" Ошибка: Файл '{file_path}' не найден!")
        return {}
        
    try:
        df = pd.read_excel(file_path, sheet_name='ис,тии рус')
        schedule = {}
        curr_day = None
        
        # Перебираем строки таблицы, где содержатся дни и предметы
        for r in range(9, len(df)):
            day_val = str(df.iloc[r, 0]).strip()
            time_val = str(df.iloc[r, 1]).strip()
            subject_val = str(df.iloc[r, 6]).strip()  # Колонка 6 = ТИИ-25-21
            
            # Определение дня недели
            if day_val != 'nan' and day_val != '':
                curr_day = day_val.split('/')[0].strip()
                if curr_day not in schedule:
                    schedule[curr_day] = []
                    
            # Добавление предмета
            if curr_day and subject_val != 'nan' and subject_val != '':
                schedule[curr_day].append({
                    "time": time_val,
                    "subject": subject_val.replace('\n', ' ')
                })
                
        return schedule
    except Exception as e:
        print(f" Ошибка парсинга Excel: {e}")
        return {}

# Первоначальная загрузка расписания в глобальную переменную
SCHEDULE = parse_excel_schedule(EXCEL_FILE)

# Карта дней недели
DAYS_MAP = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

# ----------------------------------------------------------------------
# 2. Клавиатура (Кнопки)
# ----------------------------------------------------------------------
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_today = types.KeyboardButton("📅 Сегодня")
    btn_tomorrow = types.KeyboardButton("📅 Завтра")
    btn_week = types.KeyboardButton("🗓 Вся неделя")
    btn_reload = types.KeyboardButton("🔄 Обновить из Excel")
    
    markup.add(btn_today, btn_tomorrow)
    markup.add(btn_week)
    markup.add(btn_reload)
    return markup

# ----------------------------------------------------------------------
# 3. Обработчики команд и сообщений
# ----------------------------------------------------------------------

# Обработчик /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name
    text = (
        f"👋 Привет, *{user_name}*!\n\n"
        f"🤖 Бот группы *ТИИ-25-21* (@raspisanieAI2521bot) готов к работе.\n"
        f"Выберите интересующий вариант расписания на клавиатуре ниже:"
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

# Расписание на СЕГОДНЯ
@bot.message_handler(func=lambda m: m.text == "📅 Сегодня")
def handle_today(message):
    tz = zoneinfo.ZoneInfo("Asia/Almaty")
    today_idx = datetime.datetime.now(tz).weekday()
    day_name = DAYS_MAP.get(today_idx)
    send_day_schedule(message.chat.id, day_name, f"Сегодня ({day_name})")

# Расписание на ЗАВТРА
@bot.message_handler(func=lambda m: m.text == "📅 Завтра")
def handle_tomorrow(message):
    tz = zoneinfo.ZoneInfo("Asia/Almaty")
    tomorrow_idx = (datetime.datetime.now(tz).weekday() + 1) % 7
    day_name = DAYS_MAP.get(tomorrow_idx)
    send_day_schedule(message.chat.id, day_name, f"Завтра ({day_name})")

# Расписание на ВСЮ НЕДЕЛЮ
@bot.message_handler(func=lambda m: m.text == "🗓 Вся неделя")
def handle_full_week(message):
    if not SCHEDULE:
        bot.send_message(message.chat.id, "⚠️ Расписание пустое или файл не был прочитан.")
        return

    res = "📋 *РАСПИСАНИЕ ГРУППЫ ТИИ-25-21 НА НЕДЕЛЮ*\n\n"
    work_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    
    for day in work_days:
        res += f"📌 *{day.upper()}*\n"
        if day in SCHEDULE and SCHEDULE[day]:
            for item in SCHEDULE[day]:
                res += f"  • `{item['time']}` — {item['subject']}\n"
        else:
            res += "  🎉 Занятий нет\n"
        res += "\n"
        
    bot.send_message(message.chat.id, res, parse_mode="Markdown")

# Ручное обновление данных из файловой системы
@bot.message_handler(func=lambda m: m.text == "🔄 Обновить из Excel")
def handle_reload(message):
    global SCHEDULE
    SCHEDULE = parse_excel_schedule(EXCEL_FILE)
    if SCHEDULE:
        bot.send_message(message.chat.id, "✅ Расписание успешно обновлено из Excel-файла!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось загрузить данные из файла.")

# ----------------------------------------------------------------------
# 4. Вспомогательная функция отправки расписания на конкретный день
# ----------------------------------------------------------------------
def send_day_schedule(chat_id, day_name, title_label):
    if day_name in SCHEDULE and SCHEDULE[day_name]:
        res = f"📅 *Расписание на {title_label}*:\n\n"
        for i, item in enumerate(SCHEDULE[day_name], 1):
            res += f"*{i}.* ⏰ `{item['time']}`\n📖 {item['subject']}\n\n"
    else:
        res = f"🎉 *На {title_label} занятий нет! Можно отдыхать.*"
        
    bot.send_message(chat_id, res, parse_mode="Markdown")

# ----------------------------------------------------------------------
# 5. Точка входа (Запуск бота)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(" Бот @raspisanieAI2521bot успешно запущен...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)