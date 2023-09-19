from bot import dp
from aiogram import types
from handlers import keyboard


async def start(message: types.Message):
    try:
        await message.answer('❇️ Вы уже приняты 👍', reply_markup=keyboard.mainmenu)
    except Exception as e:
        print(e)


async def keyboard_handler(message: types.message):
    print("текст123")
    try:
        match message.text:
            case "Выплаты💸":
                await message.reply('Выплаты: https://t.me/win1telegaaa')
            case "Чат💬":
                await message.reply('Чатик: https://t.me/+5UibOMGpiYMzNWQy')
            case "⚡️ЗАРЯД⚡️":
                await message.reply('⚡️⚡️⚡️ЗАРЯД НА ЕБНУТЫЙ СКАМ⚡️⚡️⚡️️')

            case "📚Мануалы":
                await message.reply('💸Мануалы: https://t.me/+ChWPHcqwK_AxMzQy')
            case "💼О проекте":
                await  message.reply("""ℹ️ Информация о проекте
📆 Мы открылись: 14.08.2023
┏ 💰 Выплаты:
┣Прямики:80%
┣Клауд:60%
┗Шантаж дп:60%""")
            case _:
                pass

    except Exception as e:
        print(e)


def register_client():
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(keyboard_handler, state='*')
