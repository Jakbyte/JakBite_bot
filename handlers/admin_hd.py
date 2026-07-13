from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from keyboard.admin_kb import admin_menu
from create_bot import ADMIN_ID
from database.requests import get_users_count, get_tasks_count


router = Router()

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Перемикаю інтерфейс...", reply_markup=ReplyKeyboardRemove())
        await message.answer(
            "😈 **Вітаю, Володарю!**\n\n"
            "Цифровий Кат слухає твоїх вказівок. Бажаєш подивитися на статистику цих нікчем чи влаштувати їм спам-терор?",
            reply_markup = admin_menu 
        )
    else:
        await message.answer("🚫 Куди свої брудні рученята тянеш? Тобі сюди зась! Повертайся в стійло.")

# Статистика
@router.message(F.text.contains('📊 Статистика бота'), F.from_user.id == ADMIN_ID)
async def show_statistics(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users_count = get_users_count()
        tasks_count = get_tasks_count()
        await message.answer(
            "📊 **АКТУАЛЬНИЙ ЗВІТ ДЛЯ НАГЛЯДАЧА**\n\n"
            f"👥 **Всього рабів у системі:** {users_count}\n"
            f"📝 **Згенеровано дедлайнів:** {tasks_count}\n\n"
            "📉 Показники ліні стабільні. Продовжуємо психологічний тиск на ледарів! ⚙️"
        )
