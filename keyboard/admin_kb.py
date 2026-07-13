from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '📊 Статистика бота'), KeyboardButton(text = '👤 Користувачі')],
        [KeyboardButton(text = '📢 Токсична розсилка'), KeyboardButton(text = '🚫 Бан / Помилування')],
        [KeyboardButton(text = '⬅️ Головне меню')]
    ],
    resize_keyboard = True
)