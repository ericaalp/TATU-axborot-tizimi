import asyncio
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject

from config import BOT_TOKEN, SUPERADMIN_IDS
from db import create_pool
from handlers import start, main, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class DbMiddleware(BaseMiddleware):
    def __init__(self, pool):
        self.pool = pool

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data["pool"] = self.pool
        return await handler(event, data)


class RoleMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        pool = data.get("pool")
        user = data.get("event_from_user")
        if user:
            if user.id in SUPERADMIN_IDS:
                data["rol"] = "superadmin"
            elif pool:
                from db import get_user
                db_user = await get_user(pool, user.id)
                data["rol"] = "foydalanuvchi" if db_user else "mehmon"
            else:
                data["rol"] = "mehmon"
        return await handler(event, data)


async def main_func():
    pool = await create_pool()
    logger.info("Ma'lumotlar bazasiga ulanildi")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware — tartib muhim: avval DB, keyin Role
    dp.update.outer_middleware(DbMiddleware(pool))
    dp.update.outer_middleware(RoleMiddleware())

    # Routerlar
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(main.router)

    # Ishga tushganda adminlarga xabar
    for admin_id in SUPERADMIN_IDS:
        try:
            await bot.send_message(admin_id, "✅ Bot ishga tushdi.")
        except Exception:
            pass

    logger.info("Bot polling boshlandi")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main_func())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
