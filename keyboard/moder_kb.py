from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

moder_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text = '📊 Статистика бота'), KeyboardButton(text = '⚠️ Нагримати на раба')],
        [KeyboardButton(text = '🧹 Очистити чат')],
        [KeyboardButton(text = '⬅️ Головне меню')]
    ],
    resize_keyboard=True
)