from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboard.admin_kb import admin_menu
from create_bot import ADMIN_ID
from database.requests import (
    get_users_count, 
    get_tasks_count, 
    get_all_user_ids, 
    get_top_lazy_users, 
    get_user_info, 
    get_user_tasks
)

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_message = State()

class SpyState(StatesGroup):
    waiting_for_user_id = State()

# --- ВХІД В АДМІНКУ ---
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

# --- СТАТИСТИКА --- 
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

# --- ТОП ЛІНТЯЇВ (КОРИСТУВАЧІ) ---
@router.message(F.text == '👤 Користувачі', F.from_user.id == ADMIN_ID)
async def show_users(message: types.Message):
    top_users = get_top_lazy_users()
    if not top_users:
        await message.answer("База порожня. Жодного раба ще не спіймано.")
        return

    text = "🏆 **ДОШКА ГАНЬБИ (Топ-10 ледарів проєкту):**\n\n"
    for i, user in enumerate(top_users, start=1):
        uid, username, first_name, comp, snooz = user
        
        # Форматуємо ім'я та юзернейм
        name_str = first_name if first_name else "Анонім"
        user_link = f"@{username}" if username else "немає юзернейму"
        
        text += f"{i}. 👤 <b>{name_str}</b> ({user_link})\n"
        text += f"   └─ 🔑 ID: <code>{uid}</code> | ✅ Закрито: {comp} | ❌ Прострочено: <b>{snooz}</b>\n\n"
    
    await message.answer(text, parse_mode="HTML")

# --- ПОЧАТОК РОЗСИЛКИ ---
@router.message(F.text == '📢 Токсична розсилка', F.from_user.id == ADMIN_ID)
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer(
        "📢 **РЕЖИМ МАСОВОГО ТЕРОРУ УВІМКНЕНО**\n\n"
        "Відправ мені повідомлення (можна текст, фото, відео або кружечок), яке отримають ВСІ користувачі.\n\n"
        "*(Щоб скасувати, напиши слово `скасувати`)*"
    )
    await state.set_state(BroadcastState.waiting_for_message)

# --- ПРИЙОМ ТА ВІДПРАВКА РОЗСИЛКИ (ОДНИМ ПОВІДОМЛЕННЯМ) ---
@router.message(BroadcastState.waiting_for_message, F.from_user.id == ADMIN_ID)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.text and message.text.lower() == 'скасувати':
        await state.clear()
        await message.answer("Розсилку скасовано. Раби можуть спати спокійно... поки що.")
        return

    user_ids = get_all_user_ids()
    sent_count = 0
    await message.answer("⏳ Починаю розсилку. Це може зайняти трохи часу...")

    header = "📢 <b>Повідомлення від JakBite (Цифровий Кат):</b>\n\n"

    for user_id in user_ids:
        try:
            if message.text:
                await message.bot.send_message(
                    chat_id=user_id,
                    text=f"{header}{message.text}",
                    parse_mode="HTML"
                )
                
            elif message.photo:
                caption = f"{header}{message.caption}" if message.caption else header
                await message.bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=caption,
                    parse_mode="HTML"
                )

            elif message.video:
                caption = f"{header}{message.caption}" if message.caption else header
                await message.bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=caption,
                    parse_mode="HTML"
                )
                
            else:
                await message.bot.send_message(
                    chat_id=user_id,
                    text=header,
                    parse_mode="HTML"
                )
                await message.copy_to(user_id)

            sent_count += 1
            await asyncio.sleep(0.05) 
            
        except Exception:
            pass
            
    await state.clear()
    await message.answer(f"✅ **Розсилка успішно завершена!**\nДоставлено повідомлень: {sent_count} з {len(user_ids)}")

# 2. РЕЖИМ ШПИГУНА (ЗАПИТ ID)
@router.message(F.text == '👁️ Шпигувати', F.from_user.id == ADMIN_ID)
async def start_spy(message: types.Message, state: FSMContext):
    await message.answer(
        "👁️ **АКТИВАЦІЯ РЕЖИМУ ШПИГУНА**\n\n"
        "Введи Telegram ID раба, за яким хочеш встановити нагляд.\n"
        "(ID можна скопіювати з меню '👤 Користувачі')\n\n"
        "*(Напиши 'скасувати' для виходу з режиму)*"
    )
    await state.set_state(SpyState.waiting_for_user_id)

# РЕЖИМ ШПИГУНА (ОБРОБКА ВВЕДЕНОГО ID)
@router.message(SpyState.waiting_for_user_id, F.from_user.id == ADMIN_ID)
async def process_spy(message: types.Message, state: FSMContext):
    if message.text.lower() == 'скасувати':
        await state.clear()
        await message.answer("Шпигунську місію скасовано. Нагляд згорнуто.", reply_markup=admin_menu)
        return

    if not message.text.isdigit():
        await message.answer("❌ Що це за шифр? Введи числовий ID користувача:")
        return

    target_id = int(message.text)
    user_info = get_user_info(target_id)

    if not user_info:
        await message.answer("❌ Такого раба немає в моїй базі даних. Перевір ID і спробуй ще раз:")
        return

    username, first_name, completed, snoozed = user_info
    tasks = get_user_tasks(target_id)

    name_str = first_name if first_name else "Анонім"
    user_link = f"@{username}" if username else "немає"
    
    report = (
        f"🕵️‍♂️ **ЗВІТ ШПИГУНА ДЛЯ НАГЛЯДАЧА** 🕵️‍♂️\n\n"
        f"👤 **Об'єкт:** {name_str} ({user_link})\n"
        f"🔑 **ID:** <code>{target_id}</code>\n"
        f"📊 **Статистика ліні:** ✅ Закрито: {completed} | ❌ Прострочено: {snoozed}\n\n"
    )

    if not tasks:
        report += "📝 **Активні таски:** Цей хитрий хробак закрив усі таски або взагалі нічого не планує! Підозріла тиша..."
    else:
        report += "📝 **Список невиконаних тасок:**\n"
        for i, task in enumerate(tasks, start=1):
            task_name, deadline = task
            report += f"  {i}. 📌 <i>\"{task_name}\"</i> (Дедлайн: {deadline})\n"

    await message.answer(report, parse_mode="HTML", reply_markup=admin_menu)
    await state.clear()  

# --- ВИХІД З АДМІНКИ ---
@router.message(F.text == '⬅️ Головне меню', F.from_user.id == ADMIN_ID)
async def exit_admin(message: types.Message):
    await message.answer("🚪 Виходимо з адмінки. Повертаю стандартний інтерфейс.", reply_markup=ReplyKeyboardRemove())