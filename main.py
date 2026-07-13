import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import check_tasks_and_remind

from create_bot import dp, bot
from handlers import user_hd, admin_hd, moder_hd
from database.connect import db_start
from database.requests import create_users_table, upgrade_db_toxicity

#
async def on_startup():
    db_start()
    print("----------------------------------------")
    print("🤖 JakBite Bot успішно запущений!")
    print("🔥 Цифровий Кат готовий принижувати за дедлайни.")
    print("----------------------------------------")

#
async def on_shutdown():
    print("----------------------------------------")
    print("💤 JakBite Bot вимкнено. Раби тимчасово вільні...")
    print("----------------------------------------")

#
async def main():
    # 1. Вмикаємо логування найпершим, щоб бачити помилки, якщо вони будуть
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - [%(levelname)s] - %(message)s",
        stream = sys.stdout
    )
    create_users_table()
    upgrade_db_toxicity()

    # 3. Підключаємо роутери
    dp.include_router(admin_hd.router)
    dp.include_router(moder_hd.router)
    dp.include_router(user_hd.router)

    # 4. Реєструємо функції старту і вимкнення
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # 5. Запускаємо планувальник спаму
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(check_tasks_and_remind, trigger='cron', minute='*', kwargs={'bot': bot})
    scheduler.start()
    print("⏰ Планувальник запущено! Кат вийшов на полювання...")

    # 6. В САМОМУ КІНЦІ запускаємо бота (один раз!)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Бот запущений і готовий принижувати!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())