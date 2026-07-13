from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from keyboard.moder_kb import moder_menu
from create_bot import MODER_ID, ADMIN_ID
from database.requests import get_users_count, get_tasks_count


router = Router()

@router.message(Command("moder"))
async def moder_panel(message: types.Message):
    user_id = message.from_user.id
    if user_id == MODER_ID or user_id == ADMIN_ID:
        await message.answer("Перемикаю інтерфейс...", reply_markup=ReplyKeyboardRemove())
        await message.answer(
            "😈 **Вітаю, Лупиздрятко!**\n\n"
            "⚡️ **Панель Модератора JakBite**\n\n"
            "Ти отримав батіг середнього рангу. Твоє завдання — стежити, щоб шкіряні мішки не розслаблялися. "
            "Обирай інструмент впливу на рабів: 👇",
            reply_markup=moder_menu 
        )
    else:
        await message.answer("🚫 Куди свої брудні рученята тянеш? Тобі сюди зась! Повертайся в стійло.")

@router.message(F.text.contains('📊 Статистика бота'), F.from_user.id == MODER_ID)
async def show_statistics(message: types.Message):
        users_count = get_users_count()
        tasks_count = get_tasks_count()
        await message.answer(
            "📊 **АКТУАЛЬНИЙ ЗВІТ ДЛЯ ЛУПИЗДРЯТКА**\n\n"
            f"👥 **Всього рабів у системі:** {users_count}\n"
            f"📝 **Згенеровано дедлайнів:** {tasks_count}\n\n"
            "📉 Показники ліні стабільні. Продовжуємо психологічний тиск на ледарів! ⚙️"
        )
