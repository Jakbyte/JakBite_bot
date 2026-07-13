from create_bot import dp
from handlers import user_hd

def register_allhandlers():
    dp.include_router(user_hd.router)