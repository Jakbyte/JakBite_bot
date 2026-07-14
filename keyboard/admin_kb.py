from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '📊 Статистика бота'), KeyboardButton(text = '👤 Користувачі')],
        [KeyboardButton(text = '👁️ Шпигувати'), KeyboardButton(text = '📢 Токсична розсилка')],
        [KeyboardButton(text = '⬅️ Головне меню')]
    ],
    resize_keyboard = True
)