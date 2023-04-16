import os
import asyncio
import logging
import openai
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, types, flags
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionMiddleware

load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_TOKEN')

key_number = -1
keys = []

router = Router()
router.message.middleware(ChatActionMiddleware())


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:

    await message.answer("В общем просто фигачьте сюда запрос к ChatGPT и все. Отвечает долго, в зависимости от количества сообщений в очереди. Может вообще крашнуться. \nНапиши сюда @santariver если:\n1. Бот не ответит\n2. Бот выдал ошибку")


@router.message()
@flags.chat_action("typing")
async def chatgpt_handler(message: types.Message) -> None:
    global key_number, keys
    key_number = (key_number + 1) % len(keys)
    openai.api_key = keys[key_number]
    
    message_text = message.text
    user_from = message.chat.username
    logging.info("Request from @{user_from}: {message}".format(
        user_from=user_from, message=message_text))
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": message_text}])
    response = completion.choices[0].message.content
    logging.info("Response for @{user_from}: {response}".format(
        user_from=user_from, response=response))
    await message.answer(response)
    # logging.error("Response for @{user_from}: {respons e}".format(
    #     user_from=user_from, response="ChatGTP response error"))
    # await message.answer('Ошибка при обрашении к ChatGPT. Попробуй еще раз')



async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    dp.message.middleware(ChatActionMiddleware())

    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    keys = os.getenv('OPENAI_API_TOKENS').split(',')
    logging.basicConfig(
        filename='chatgpt.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    asyncio.run(main())
