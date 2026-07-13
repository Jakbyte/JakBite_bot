from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
DB_NAME = os.getenv("DB_NAME")

ADMIN_ID = int(os.getenv("ADMIN_ID"))
MODER_ID = int(os.getenv("MODER_ID"))
