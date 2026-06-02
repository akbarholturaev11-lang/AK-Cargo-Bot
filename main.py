import asyncio
import logging

from aiogram import Bot, Dispatcher
from middlewares.channel_required import ChannelRequiredMiddleware
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.init_db import init_db
from handlers import (
    admin_broadcast,
    admin_bulk,
    admin_delivery,
    admin_menu,
    admin_parcels,
    admin_settings,
    admin_status,
    admin_warehouses,
    auth,
    calculator,
    delivery,
    my_parcels,
    operator,
    parcel_search,
    prohibited_goods,
    profile,
    start,
    user_menu,
    warehouses,
)
from services.settings import seed_default_settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ROUTERS = (
    admin_broadcast.router,
    start.router,
    auth.router,
    user_menu.router,
    parcel_search.router,
    prohibited_goods.router,
    my_parcels.router,
    calculator.router,
    profile.router,
    warehouses.router,
    delivery.router,
    operator.router,
    admin_menu.router,
    admin_parcels.router,
    admin_status.router,
    admin_bulk.router,
    admin_warehouses.router,
    admin_delivery.router,
    admin_settings.router,
)


async def on_startup() -> None:
    logger.info("Initializing database")
    await init_db()
    logger.info("Seeding default settings")
    await seed_default_settings()
    logger.info("Startup completed")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    await on_startup()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    channel_required_middleware = ChannelRequiredMiddleware()
    dp.message.middleware(channel_required_middleware)
    dp.callback_query.middleware(channel_required_middleware)

    dp.include_routers(*ROUTERS)

    logger.info("Starting Akcorgo bot")
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Stopping Akcorgo bot")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
