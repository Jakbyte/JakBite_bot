import random
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Додаємо імпорт стікерів
from data.vocabulary import TOXIC_QUOTES, STICKERS
# Додай сюди свою функцію для отримання режиму юзера (Нянька/Кат/УЛЬТРА-САДИСТ)
from database.requests import get_all_active_tasks, get_user_toxicity


async def check_tasks_and_remind(bot: Bot):
    print("⏳ Планувальник робить перевірку...")
    tasks = get_all_active_tasks()
    now = datetime.now()
    
    # Словник для адаптації оформлення під кожен режим
    UI_THEMES = {
        "Нянька": {
            "title": "🌸 **Нагадувалочка про тасочку!** 🌸",
            "author": "Твоя Нянька"
        },
        "Кат": {
            "title": "🚨 **ДЕДЛАЙН ГОРИТЬ, Ледащо!** 🚨",
            "author": "Кат"
        },
        "УЛЬТРА-САДИСТ": {
            "title": "🔥 **ТИ ПРОГРАЄШ ЦЕЙ БІЙ! ЧАС ВИЙШОВ!** 🔥",
            "author": "УЛЬТРА-САДИСТ"
        }
    }

    for task in tasks:
        task_id, user_id, category, task_text, deadline_str, remind_offset = task
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        send_message = False

        if remind_offset >= 0:
            target_time = deadline - timedelta(minutes=remind_offset)
            if (target_time.year == now.year and
                target_time.month == now.month and
                target_time.day == now.day and
                target_time.hour == now.hour and
                target_time.minute == now.minute):
                send_message = True

        # Спам кожні 5 хв
        elif remind_offset == -5:
            if now.minute % 5 == 0:
                send_message = True

        # Повідомлення з inline кнопками
        if send_message:
            # 1. Отримуємо поточний режим користувача (якщо немає в БД — ставимо "Кат")
            try:
                user_mode = get_user_toxicity(user_id)
            except Exception:
                user_mode = "Кат"
                
            if user_mode not in ["Нянька", "Кат", "УЛЬТРА-САДИСТ"]:
                user_mode = "Кат"

            # 2. Вибираємо випадкову фразу та стікер відповідно до режиму
            quotes_pool = TOXIC_QUOTES.get(user_mode, TOXIC_QUOTES["Кат"])
            random_quote = random.choice(quotes_pool)
            
            sticker_pool = STICKERS.get(user_mode, [])
            chosen_sticker = random.choice(sticker_pool) if sticker_pool else None

            # 3. Адаптуємо оформлення тексту
            theme = UI_THEMES.get(user_mode, UI_THEMES["Кат"])
            
            text = (
                f"{theme['title']}\n\n"
                f"📂 Група: **[{category}]**\n"
                f"📝 Що зробити: _{task_text}_\n"
                f"⏰ Час Ч: **{deadline_str}**\n\n"
                f"💬 **Від {theme['author']}:** {random_quote}"
            )
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я виконав, відчепись! 😤", callback_data=f"complete_{task_id}")],
                [InlineKeyboardButton(text="❌ Я не встиг, ще 5 хв! ⏳", callback_data=f"snooze_{task_id}")],
            ])
            
            try:
                # 4. Спочатку надсилаємо стікер (загорнутий у try/except, щоб бот не впав через битий file_id)
                if chosen_sticker:
                    try:
                        await bot.send_sticker(chat_id=user_id, sticker=chosen_sticker)
                    except Exception as sticker_error:
                        print(f"⚠️ Не вдалося надіслати стікер для {user_id}: {sticker_error}")
                
                # 5. Надсилаємо основне повідомлення
                await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)
                
            except Exception as e:
                print(f"Не вдалося надіслати повідомлення {user_id}: {e}")

