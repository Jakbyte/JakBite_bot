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

# --- СТАТИСТИКА ДЛЯ МОДЕРАТОРА ---
@router.message(F.text == '📊 Статистика бота', F.from_user.id == MODER_ID)
async def mod_show_statistics(message: types.Message):
    users_count = get_users_count()
    tasks_count = get_tasks_count()
    await message.answer(
        "📊 **ЗВІТ ДЛЯ МОЛОДШОГО НАГЛЯДАЧА**\n\n"
        f"👥 **Підконтрольних душ:** {users_count}\n"
        f"📝 **Активних батогів (дедлайнів):** {tasks_count}\n\n"
        "Стеж за показниками. Якщо лінь почне перемагати — доклади Володарю!"
    )

# --- СПИСОК КОРИСТУВАЧІВ ДЛЯ МОДЕРАТОРА ---
@router.message(F.text == '👤 Користувачі', F.from_user.id == MODER_ID)
async def mod_show_users(message: types.Message):
    top_users = get_top_lazy_users()
    if not top_users:
        await message.answer("У твоїй зміні поки немає рабів. Пощастило тобі.")
        return

    text = "🏆 **СПИСОК ЛЕДАРІВ НА ТВОЄМУ ЧЕРГУВАННІ:**\n\n"
    for i, user in enumerate(top_users, start=1):
        uid, username, comp, snooz = user
        name = f"@{username}" if username else f"ID:{uid}"
        text += f"{i}. {name} | ✅ Виконано: {comp} | ❌ Прострочено: {snooz}\n"
    
    await message.answer(text)

# --- ВИХІД З ПАНЕЛІ МОДЕРАТОРА ---
@router.message(F.text == '⬅️ Головне меню', F.from_user.id == MODER_ID)
async def mod_exit(message: types.Message):
    await message.answer("🚪 Повертаєшся до звичайної роботи. Батіг здано на склад.", reply_markup=ReplyKeyboardRemove())