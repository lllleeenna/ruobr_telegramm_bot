import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.config import load_config, Config
from handlers.user_handlers import register_user_handlers
from keyboards.main_menu import set_main_menu
from aiogram.fsm.storage.redis import RedisStorage

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher) -> None:
    register_user_handlers(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')
    config: Config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    storage: RedisStorage = RedisStorage.from_url(url=config.db.db_link)
    dp: Dispatcher = Dispatcher(storage=storage)

    await set_main_menu(bot)

    register_all_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
