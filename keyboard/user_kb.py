from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Головне меню
main_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '📂 Мої Групи'), KeyboardButton(text = '📋 Мої завдання')],
        [KeyboardButton(text = '📊 Мій Профіль'), KeyboardButton(text = '⚙️ Налаштування')],
        [KeyboardButton(text = '🤖 Про бота')]
    ],
    resize_keyboard = True
)

# Меню категорій
categories_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '📚 Навчання'), KeyboardButton(text = '💼 Робота')],
        [KeyboardButton(text = '🏡 Особисте')],
        [KeyboardButton(text = '⬅️ Головне меню')]
    ],
    resize_keyboard = True
)

# Назад
back_to_categories_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '⬅️ Назад до категорій')]
    ],
    resize_keyboard = True
)

tasks_inline_menu = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text = "➕ Додати завдання", callback_data = "add_task"),
            InlineKeyboardButton(text = "❌ Видалити завдання", callback_data = "delete_task")
        ]
    ]
)

def get_remind_keyboard():
    """Генерація кнопок для вибору часу нагадування"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Вчасно ⏱", callback_data="remind_0")
    #builder.button(text="За 1 хв 🏃", callback_data="remind_1")
    builder.button(text="Кожні 5 хв 🔄", callback_data="remind_-5") 
    builder.button(text="За 15 хв 🏃", callback_data="remind_15")
    builder.button(text="За 30 хв ⏰", callback_data="remind_30")
    builder.button(text="За 1 год ⏳", callback_data="remind_60")
    builder.button(text="За 2 год ⏳", callback_data="remind_120") 
    builder.button(text="За 1 день 📅", callback_data="remind_1440")

    builder.adjust(1, 2, 2, 2) 
    return builder.as_markup()

def get_hours_keyboard():
    """Генерація кнопок для вибору годин (сітка 4х6)"""
    builder = InlineKeyboardBuilder()
    for hour in range(24):
        h_str = f"{hour:02d}"
        builder.button(text=f"{h_str}:00", callback_data=f"hour_{h_str}")
    builder.adjust(4)
    return builder.as_markup()

def get_minutes_keyboard():
    """Генерація кнопок для вибору хвилин (крок 15 хв)"""
    builder = InlineKeyboardBuilder()
    for minute in [0, 15, 30, 45]:
        m_str = f"{minute:02d}"
        builder.button(text=f":{m_str}", callback_data=f"min_{m_str}")
    builder.adjust(2)
    return builder.as_markup()

# Клавіатуцра для вибору категорії завдань
def get_task_filter_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text = "Всі разом 🌍", callback_data = "show_cat_Усі")
    builder.button(text = "📚 Навчання", callback_data = "show_cat_Навчання")
    builder.button(text = "💼 Робота", callback_data = "show_cat_Робота")
    builder.button(text = "🏡 Особисте", callback_data = "show_cat_Особисте")
    builder.button(text="⬅️ Закрити меню", callback_data="close_inline_menu")
    builder.adjust(1,3, 1)
    return builder.as_markup()

# Клавіатура для керування завданям
def get_task_manage_keyboard(task_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text = "✅ Завершити", callback_data = f"done_task_{task_id}")
    builder.button(text = "📅 Змінити час", callback_data = f"edit_time_{task_id}")
    builder.button(text = "❌ Видалити", callback_data = f"del_task_{task_id}")
    builder.button(text="⬅️ Сховати таску", callback_data="close_inline_menu")
    builder.adjust(2,1,1)
    return builder.as_markup()
    
# Кнопки для профілю
def get_profile_keyboard(share_text: str):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Скинути статистику", callback_data="reset_stats")
    builder.button(text="📢 Поділитися ганьбою", switch_inline_query=share_text)
    builder.adjust(1) 
    return builder.as_markup()

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_toxicity_keyboard(current_mode: str = "Кат"):
    builder = InlineKeyboardBuilder()
    modes = {
        "Нянька": {
            "cb": "tox__Нянька", 
            "text": "👼 Нянька (Лагідно 🌸)"
        },
        "Кат": {
            "cb": "tox__Кат", 
            "text": "🤬 Кат (Стандарт 😈)"
        },
        "УЛЬТРА-САДИСТ": {
            "cb": "tox__Ультра", 
            "text": "💀 УЛЬТРА-САДИСТ (треш 💀)"
        }
    }
    
    for mode_name, data in modes.items():
        if mode_name == current_mode:
            btn_text = f"✅ {data['text']}"
        else:
            btn_text = data['text']
            
        builder.button(text=btn_text, callback_data=data["cb"])
        
    builder.adjust(1) 
    return builder.as_markup()