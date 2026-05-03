import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import TOKEN
from database import init_db
from handlers import router
from middlewares import RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Rate limiting
dp.message.middleware(RateLimitMiddleware(interval=1))

# Подключаем роутер с хендлерами
dp.include_router(router)

# Глобальный error handler
@dp.errors()
async def global_error_handler(event: ErrorEvent):
    logging.error(f"🔥 Глобальная ошибка: {event.exception}", exc_info=True)
    return True

async def main():
    try:
        init_db()
        print("✅ База данных готова")
    except Exception as e:
        logging.error(f"❌ Ошибка БД: {e}", exc_info=True)
        return
    
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())