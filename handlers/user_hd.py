from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random

from keyboard.user_kb import (
    main_menu, 
    categories_menu, 
    back_to_categories_menu, 
    tasks_inline_menu,
    get_hours_keyboard,
    get_minutes_keyboard,
    get_remind_keyboard,
    get_task_filter_keyboard,
    get_task_manage_keyboard,
    get_profile_keyboard,
    get_toxicity_keyboard
)
from database.requests import (
    add_user, 
    add_task_to_db, 
    get_user_tasks, 
    delete_task, 
    postpone_task, 
    get_tasks_by_category,
    update_task_deadline,
    update_stat,
    get_user_stats,
    reset_user_stats,
    set_user_toxicity,
    get_user_toxicity
)
from data.vocabulary import TOXIC_QUOTES, SNOOZE_QUOTES, SUCCESS_QUOTES, SHARE_TEMPLATES, NAVIGATION_TEXTS

router = Router()

class TaskStates(StatesGroup):
    waiting_for_task_text = State()
    waiting_for_task_date = State()
    waiting_for_task_hour = State()
    waiting_for_task_minute = State()
    waiting_for_remind_time = State()
    waiting_for_edit_date = State()
    waiting_for_edit_hour = State()
    waiting_for_edit_minute = State()


# =====================================================================
# ГОЛОВНЕ МЕНЮ ТА ПРОФІЛЬ
# =====================================================================

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "О, чергове ліниве створіння приповзло... 🙄\n\n"
        "Я — **JakBite**, твий персональний кошмар і наглядач за дедлайнами. "
        "Я тут не для того, щоб хвалити твої мізерні успіхи. Моя робота — знущатися з тебе, поки ты не закриєш свої таски.\n\n"
        "Тисни кнопки внизу, якщо ще не повністю атрофувався від прокрастинації: 👇",
        reply_markup=main_menu
    )

@router.message(F.text == '📊 Мій Профіль')
async def show_profile(message: types.Message):
    stats = get_user_stats(message.from_user.id)
    active_tasks = get_user_tasks(message.from_user.id)
    active_count = len(active_tasks) if active_tasks else 0

    if not stats:
        completed, snoozed = 0, 0
    else:
        completed, snoozed = stats
        
    total_actions = completed + snoozed
    if total_actions == 0:
        proc_percent = 0
    else:
        proc_percent = int((snoozed / total_actions) * 100)

    red_blocks = proc_percent // 10
    green_blocks = 10 - red_blocks
    progress_bar = "🟥" * red_blocks + "🟩" * green_blocks

    badges = []
    if completed == 0 and snoozed == 0:
        badges.append("🥚 Амеба (ще нічого не робив)")
        rank = "Амеба"
    else:
        if snoozed >= 5:
            badges.append("🐌 Магістр Прокрастинації")
            rank = "Магістр Прокрастинації"
        if snoozed >= 15:
            badges.append("🤡 Король Відмазок")
            rank = "Король Відмазок"
        if completed >= 3:
            badges.append("🥉 Подає надії")
            rank = "Подає надії"
        if completed >= 10:
            badges.append("🗿 Термінатор дедлайнів")
            rank = "Термінатор дедлайнів"
        
        if not badges:
            badges.append("👤 Звичайний ледащо")
            rank = "Звичайний ледащо"

    badges_text = "\n".join([f"  • {b}" for b in badges])

    text = (
        f"👤 **ТВОЯ ДОШКА ГАНЬБИ:**\n\n"
        f"🔥 **Активні борги:** {active_count} шт.\n"
        f"✅ **Виконано завчасно:** {completed}\n"
        f"⏳ **Відкладено (злякався):** {snoozed}\n\n"
        f"📈 **Індекс ліні: {proc_percent}%**\n"
        f"[{progress_bar}]\n\n"
        f"🏆 **Твої здобутки:**\n{badges_text}"
    )
    
    # 🌟 ДИНАМІЧНИЙ РЕЖИМ: Отримуємо поточний режим токсичності користувача
    user_mode = get_user_toxicity(message.from_user.id) or "Кат"
    
    # Перевірка на всяк випадок, якщо в базі щось не те
    if user_mode not in ["Нянька", "Кат", "УЛЬТРА-САДИСТ"]:
        user_mode = "Кат"

    # Беремо потрібний список шаблонів зі словника
    current_templates = SHARE_TEMPLATES.get(user_mode, SHARE_TEMPLATES["Кат"])
    
    # Вибираємо випадковий шаблон із отриманого списку
    template = random.choice(current_templates)
    
    # Форматуємо текст для кнопки поширення
    share_text = template.format(proc_percent=proc_percent, rank=rank)
    
    await message.answer(text, reply_markup=get_profile_keyboard(share_text))

@router.callback_query(F.data == "reset_stats")
async def reset_stats_handler(callback: types.CallbackQuery):
    reset_user_stats(callback.from_user.id)
    await callback.message.edit_text(
        "🗑 **Статистику скинуто!**\n\n"
        "Історія очищена. Але ми обидва знаємо, що ти знову почнеш відкладати все на потім. "
        "Нове життя з понеділка, так-так... 🙄"
    )
    await callback.answer("Дані видалено!")

@router.message(F.text == '🤖 Про бота')
async def about_bot(message: types.Message):
    await message.answer(
        "🤖 **JakBite v1.0 — Твій цифровий наглядач**\n\n"
        "Я створений не для того, щоб надсилати тобі милі котики чи гладити по голівці. "
        "Моя єдина місія — **випалювати твою лінь каленим залізом** і знущатися з тебе, поки всі твої дедлайни не будуть закриті. 🔥\n\n"
        "🛡 **Мої головні фічі:**\n"
        "• ⛓ *Нульова толерантність до відмазок.*\n"
        "• 🧠 *Пам'ять як у слона* — я запишу кожну твою лабу чи таску по роботі.\n"
        "• 📈 *Психологічний тиск* — нагадуватиму про борги так часто, що тобі простіше буде їх зробити, ніж терпіти мене.\n\n"
        "⚙️ *Статус системи:* Працює на 100% потужності.\n"
        "🔋 *Рівень токсичності:* Максимальний.\n\n"
        "Досить витріщатися на цей text, іди працюй! 💀"
    )

# =====================================================================
# НАЛАШТУВАННЯ ТА СТІКЕРИ
# =====================================================================

@router.message(F.text == '⚙️ Налаштування')
async def setting_menu(message: types.Message):
    curent_tox = get_user_toxicity(message.from_user.id) or "Кат"
    await message.answer(
        f"⚙️ **Налаштування наглядача**\n\n"
        f"Поточний режим: **{curent_tox}**\n\n"
        f"Обери, як сильно я маю над тобою знущатися:",
        reply_markup=get_toxicity_keyboard(curent_tox)
    )

@router.callback_query(F.data.startswith("tox__"))
async def change_toxicity_handler(callback: types.CallbackQuery):
    level = callback.data.split("__")[1]
    if level == "Ультра":
        level = "УЛЬТРА-САДИСТ"
    set_user_toxicity(callback.from_user.id, level)
    msg = f"⚙️ **Налаштування наглядача**\n\n✅ Режим успішно змінено на: **{level}**\n"
    
    if level == "Нянька":
        msg += "\nДобре, сонечко, буду нагадувати лагідно. 🥺"
    elif level == "Кат":
        msg += "\nПовертаємося до класичного знущання. Ледацюго, готуйся. 😈"
    elif level == "УЛЬТРА-САДИСТ":
        msg += "\nГОТУЙСЯ СТРАЖДАТИ, НІКЧЕМО! 🔥💀"

    await callback.message.edit_text(
        msg,
        reply_markup=get_toxicity_keyboard(level)
    )

@router.message(F.sticker)
async def catch_sticker_id(message: types.Message):
    sticker_id = message.sticker.file_id
    await message.answer(
         f"🎯 **Спіймав стікер!**\n\n"
        f"Ось його ID:\n`{sticker_id}`\n\n"
        f"Скопіюй цей код і додай його у свій планувальник, щоб я міг ним спамити."
    )

# =====================================================================
# ВІДОБРАЖЕННЯ ТА КЕРУВАННЯ ЗАВДАННЯМИ (ІНЛАЙН)
# =====================================================================

@router.message(F.text == '📋 Мої завдання')
async def show_my_tasks(message: types.Message):
    await message.answer("👀 Які саме борги ти хочеш подивитися?", reply_markup=get_task_filter_keyboard())

@router.callback_query(F.data.startswith("show_cat_"))
async def show_filtered_tasks(callback: types.CallbackQuery):
    category = callback.data.split("_")[2]
    tasks = get_tasks_by_category(callback.from_user.id, category) 
    await callback.message.delete()
    
    if not tasks:
        await callback.message.answer(f"У категорії **{category}** порожньо. Ти або молодець, або просто ледащо, яке нічого не планує. 🤷‍♂️")
        return
        
    await callback.message.answer(f"📂 Твої завдання у категорії: **{category}**")

    for task in tasks:
        task_id, cat, task_text, deadline = task 
        text = f"📝 **{task_text}**\n⏰ Дедлайн: {deadline}"
        
        if category == "Усі":
            text = f"📂 [{cat}]\n" + text
            
        await callback.message.answer(text, reply_markup=get_task_manage_keyboard(task_id))

@router.callback_query(F.data == "close_inline_menu")
async def close_inline_menu_handler(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("Втікаєш від своїх проблем? Ну-ну, дедлайни тебе все одно знайдуть! 😈", show_alert=False)

# Дострокове завершення завдання з урахуванням токсичності
@router.callback_query(F.data.startswith("done_task_"))
async def done_task_early(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[2])
    delete_task(task_id)
    update_stat(callback.from_user.id, 'completed')
    
    # 🌟 ДИНАМІЧНИЙ РЕЖИМ: Отримуємо режим користувача
    user_mode = get_user_toxicity(callback.from_user.id) or "Кат"
    if user_mode not in ["Нянька", "Кат", "УЛЬТРА-САДИСТ"]:
        user_mode = "Кат"

    # Беремо фразу з SUCCESS_QUOTES відповідно до режиму
    praise_pool = SUCCESS_QUOTES.get(user_mode, SUCCESS_QUOTES["Кат"])
    praise = random.choice(praise_pool)
    
    await callback.message.edit_text(f"~~{callback.message.text}~~\n\n{praise}")

@router.callback_query(F.data.startswith("del_task_"))
async def delete_task_handler(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[2])
    delete_task(task_id)
    await callback.message.edit_text("🗑 Завдання видалено. Злився, так? Ну буває...")

@router.callback_query(F.data.startswith("edit_time_"))
async def edit_time_start(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[2])
    await state.update_data(edit_task_id=task_id)
    await state.set_state(TaskStates.waiting_for_edit_date)
    calendar_markup = await SimpleCalendar().start_calendar()
    await callback.message.edit_text(
        "📅 **Обери нову дату для цього завдання:**\n\n"
        "*(Знову відкладаєш? Я так і знав...)*",
        reply_markup=calendar_markup
    )

@router.callback_query(SimpleCalendarCallback.filter(), TaskStates.waiting_for_edit_date)
async def process_edit_date(callback: types.CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        formatted_date = date.strftime("%Y-%m-%d")
        await state.update_data(edit_date=formatted_date)
        await state.set_state(TaskStates.waiting_for_edit_hour)
        await callback.message.edit_text(
            f"📅 Нова дата: **{formatted_date}**\n\n"
            "🕒 **Тепер обери нову годину:**",
            reply_markup=get_hours_keyboard()
        )

@router.callback_query(F.data.startswith("hour_"), TaskStates.waiting_for_edit_hour)
async def process_edit_hour(callback: types.CallbackQuery, state: FSMContext):
    chosen_hour = callback.data.split("_")[1]
    await state.update_data(edit_hour=chosen_hour)
    await state.set_state(TaskStates.waiting_for_edit_minute)
    await callback.message.edit_text(
        f"🕒 Нова година: **{chosen_hour}:00**\n\n"
        "⏱ **Обери хвилини:**",
        reply_markup=get_minutes_keyboard()
    )

@router.callback_query(F.data.startswith("min_"), TaskStates.waiting_for_edit_minute)
async def process_edit_minute(callback: types.CallbackQuery, state: FSMContext):
    chosen_minute = callback.data.split("_")[1]
    user_data = await state.get_data()
    task_id = user_data.get("edit_task_id")
    edit_date = user_data.get("edit_date")
    edit_hour = user_data.get("edit_hour")
    new_deadline = f"{edit_date} {edit_hour}:{chosen_minute}"
    
    update_task_deadline(task_id, new_deadline)
    update_stat(callback.from_user.id, 'snoozed')
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ **Дедлайн успішно перенесено на {new_deadline}!**\n\n"
        "Сподіваюсь, цього разу ти дійсно все зробиш, а не будеш як завжди... 🙄"
    )

# Відкладення завдання (snooze) з урахуванням токсичності
@router.callback_query(F.data.startswith("snooze_"))
async def snooze_task_handler(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1]) 
    postpone_task(task_id, 5) 
    update_stat(callback.from_user.id, 'snoozed')
    
    # 🌟 ДИНАМІЧНИЙ РЕЖИМ: Отримуємо режим для підбору правильного "компліменту"
    user_mode = get_user_toxicity(callback.from_user.id) or "Кат"
    if user_mode not in ["Нянька", "Кат", "УЛЬТРА-САДИСТ"]:
        user_mode = "Кат"

    # Якщо SNOOZE_QUOTES у тебе вже структурований як словник — беремо з нього, якщо ні — залишаємо звичайний список
    if isinstance(SNOOZE_QUOTES, dict):
        quote_pool = SNOOZE_QUOTES.get(user_mode, SNOOZE_QUOTES["Кат"])
    else:
        quote_pool = SNOOZE_QUOTES
        
    quote = random.choice(quote_pool)
    
    # Словник підписів автора для краси
    authors = {"Нянька": "Нянька каже", "Кат": "Кат каже", "УЛЬТРА-САДИСТ": "УЛЬТРА-САДИСТ реве"}
    current_author = authors.get(user_mode, "Кат каже")

    try:
        await callback.message.delete()
    except Exception:
        try:
            await callback.message.edit_text(
                f"{callback.message.text}\n\n✅ **[ГРІХ ЗАРАХОВАНО: ДЕДЛАЙН ПЕРЕНЕСЕНО]**"
            )
        except Exception:
            pass
            
    await callback.message.answer(
        f"⏳ Дедлайн зсунуто на 5 хвилин.\n\n"
        f"💬 **{current_author}:** {quote}"
    )


# =====================================================================
# НАВІГАЦІЯ ТА КАТЕГОРІЇ
# =====================================================================

@router.message(F.text == '📂 Мої Групи')
async def my_groups(message: types.Message):
    user_mode = get_user_toxicity(message.from_user.id) or "Кат"
    
    # Отримуємо СПИСОК фраз для поточного режиму і беремо одну випадкову
    text_list = NAVIGATION_TEXTS["groups"].get(user_mode, NAVIGATION_TEXTS["groups"]["Кат"])
    text = random.choice(text_list)
    
    await message.answer(text, reply_markup=categories_menu)

@router.message(F.text == '⬅️ Головне меню')
async def back_to_main_menu(message: types.Message):
    user_mode = get_user_toxicity(message.from_user.id) or "Кат"
    
    # Отримуємо СПИСОК фраз для поточного режиму і беремо одну випадкову
    text_list = NAVIGATION_TEXTS["main_menu"].get(user_mode, NAVIGATION_TEXTS["main_menu"]["Кат"])
    text = random.choice(text_list)
    
    await message.answer(text, reply_markup=main_menu)

@router.message(F.text == '⬅️ Назад до категорій')
async def cmd_back_to_categories(message: types.Message):
    user_mode = get_user_toxicity(message.from_user.id) or "Кат"
    
    # Отримуємо СПИСОК фраз для поточного режиму і беремо одну випадкову
    text_list = NAVIGATION_TEXTS["categories"].get(user_mode, NAVIGATION_TEXTS["categories"]["Кат"])
    text = random.choice(text_list)
    
    await message.answer(text, reply_markup=categories_menu)

@router.message(F.text == '📚 Навчання')
async def learning_category(message: types.Message, state: FSMContext):
    await state.update_data(chosen_category="Навчання")
    await message.answer(
        "Ти зайшов у групу: **Навчання**.\n\n"
        "🎓 Вирішив підтягнути свої мізерні знання? Ну давай подивимось, які лабораторні, курсові чи "
        "дедлайни ти успішно ігноруєш, поки твої одногрупники хоча б намагаються вчитися. \n\n"
        "📝 **Напиши текст завдання, яке треба зробити:**",
        reply_markup=back_to_categories_menu
    )
    await message.answer("Обери дію над завданнями цієї групи: 👇", reply_markup=tasks_inline_menu)

@router.message(F.text == '💼 Робота')
async def work_category(message: types.Message, state: FSMContext):
    await state.update_data(chosen_category="Робота")
    await message.answer(
        "Ти зайшов у групу: **Робота**.\n\n"
        "💸 Гроші самі себе не зароблять, хоча дивлячись на твою продуктивність, ти працюєш за спасибі.\n"
        "Тут з'являться таски, які твій менеджер або замовник чекають ще з минулого тижня.\n\n"
        "🔥 Ворушись, пролетаріат, скоро дедлайн!\n\n"
        "📝 **Напиши текст завдання, яке треба зробити:**",
        reply_markup=back_to_categories_menu
    )
    await message.answer("Обери дію над завданнями цієї групи: 👇", reply_markup=tasks_inline_menu)

@router.message(F.text == '🏡 Особисте')
async def personal_category(message: types.Message, state: FSMContext):
    await state.update_data(chosen_category="Особисте")
    await message.answer(
        f"Ти зайшов у групу: **{message.text}**.\n\n"
        "Особисті справи? Це ті, які ти відкладаєш місяцями? Прибрати в кімнаті, купити шкарпетки чи нарешті сходити до лікаря? "
        "Твоє життя тріщить по швах від ліні, але я змушу тебе закрити ці хвости. Жодної пощади навіть до побуту! 🧹💀",
        reply_markup=back_to_categories_menu
    )
    await message.answer("Обери дію над завданнями цієї групи: 👇", reply_markup=tasks_inline_menu)


# =====================================================================
# ХЕНДЛЕРИ ДОДАВАННЯ ЗАВДАННЯ 
# =====================================================================

@router.callback_query(F.data == "add_task")
async def start_add_task(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TaskStates.waiting_for_task_text)
    await callback.answer()
    await callback.message.answer(
        "📝 **Режим запису активовано.**\n\n"
        "Напиши мені, яке завдання ти постійно відкладаєш? (Наприклад: *Повчити Python*, *Сходити в зал*)"
    )

@router.message(TaskStates.waiting_for_task_text)
async def process_task_text(message: types.Message, state: FSMContext):
    await state.update_data(chosen_task_text=message.text)
    await state.set_state(TaskStates.waiting_for_task_date)
    calendar_markup = await SimpleCalendar().start_calendar()
    await message.answer(
        "📅 **Тепер обери дату дедлайну на календарі нижче:**",
        reply_markup=calendar_markup
    )

@router.callback_query(SimpleCalendarCallback.filter(), TaskStates.waiting_for_task_date)
async def process_task_date(callback: types.CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        formatted_date = date.strftime("%Y-%m-%d")
        await state.update_data(chosen_date=formatted_date)
        await state.set_state(TaskStates.waiting_for_task_hour)
        await callback.message.edit_text(
            f"📅 Дата обрана: **{formatted_date}**\n\n"
            "🕒 **Тепер обери годину для дедлайну:**",
            reply_markup=get_hours_keyboard()
        )

@router.callback_query(F.data.startswith("hour_"), TaskStates.waiting_for_task_hour)
async def process_task_hour(callback: types.CallbackQuery, state: FSMContext):
    chosen_hour = callback.data.split("_")[1]
    await state.update_data(chosen_hour=chosen_hour)
    await state.set_state(TaskStates.waiting_for_task_minute)
    await callback.message.edit_text(
        f"🕒 Година обрана: **{chosen_hour}:00**\n\n"
        "⏱ **Обери хвилини:**",
        reply_markup=get_minutes_keyboard()
    )

@router.callback_query(F.data.startswith("min_"), TaskStates.waiting_for_task_minute)
async def process_task_minute(callback: types.CallbackQuery, state: FSMContext):
    chosen_minute = callback.data.split("_")[1]
    await state.update_data(chosen_minute=chosen_minute)
    await state.set_state(TaskStates.waiting_for_remind_time)
    await callback.message.edit_text(
        "🔔 **Коли тобі нагадати про це, щоб ти знову не провтикав?**",
        reply_markup=get_remind_keyboard()
    )

@router.callback_query(F.data.startswith("remind_"), TaskStates.waiting_for_remind_time)
async def process_remind_time(callback: types.CallbackQuery, state: FSMContext):
    remind_offset = int(callback.data.split("_")[1]) 
    user_data = await state.get_data()
    category = user_data.get("chosen_category", "Загальне")
    task_text = user_data.get("chosen_task_text")
    task_date = user_data.get("chosen_date")
    task_hour = user_data.get("chosen_hour")
    chosen_minute = user_data.get("chosen_minute")
    user_id = callback.from_user.id
    final_deadline = f"{task_date} {task_hour}:{chosen_minute}"
    
    add_task_to_db(
        user_id=user_id, 
        category=category, 
        task_text=task_text, 
        deadline=final_deadline, 
        remind_offset=remind_offset
    )
    
    await state.clear()
    await callback.message.delete()
    
    offset_text = {
        0: "В момент дедлайну",
        5: "За 5 хвилин",
        -5: "Кожні 5 хвилин (спам-режим активовано 😈)",
        15: "За 15 хвилин",
        30: "За 30 хвилин",
        60: "За 1 годину",
        120: "За 2 години",
        1440: "За 1 день"
    }.get(remind_offset, "Невідомо")
    
    await callback.message.answer(
        f"✅ **Завдання успішно додано в групу [{category}], нікчемо!**\n\n"
        f"📝 Що зробити: «_{task_text}_»\n"
        f"⏰ Кінцевий дедлайн: **{final_deadline}**\n"
        f"🔔 Нагадаю: **{offset_text}**\n\n"
        "Спробуй тільки проґавити цей час... Годинник цокає! ⏱😈",
        reply_markup=main_menu
    )