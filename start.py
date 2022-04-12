import logging,asyncio,random,json

from config_reader import load_config
from avito import Avito

from aiogram import Bot, types, Dispatcher
from aiogram.types import BotCommand
from aiogram.dispatcher.filters import Text, IDFilter

logging.basicConfig(format='\n%(asctime)s\n%(levelname)s:%(name)s:%(message)s\n',datefmt='%d/%m/%Y %I:%M:%S %p',level=logging.INFO)
config = load_config("config.ini")
avito=Avito(config)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/key", description="Получение ключa анти-бана"),
        BotCommand(command="/start", description="Запуск бота")
    ]
    await bot.set_my_commands(commands)


async def cmd_start(message: types.Message, avito=avito):
    avito.message=message
    await avito.start_browser()


async def main(config):
    bot=Bot(token=config.tg_bot.token)
    dp=Dispatcher(bot)
    dp.register_message_handler(cmd_start,  commands="start")
    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main(config))
