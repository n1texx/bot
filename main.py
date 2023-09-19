
import sqlite3
import datetime

import aiogram
from aiogram import executor, types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from magic_filter.operations import call
from datetime import timedelta


from handlers import keyboard

# __________________________Данные бота__________________________
admin_id = 2018079386 # Id админа
token = "6513775298:AAHFE_DqDW3rgWdR_hhaTkYetRNCvZXcGIE"  # Токен бота
chat_link = "https://t.me/+BI-3nBV-yn8xODk6"  # Ссылка на чат
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# __________________________Вопросы__________________________
question_1 = "Вы пришли с рекламы (с какой?) или же от друга (ссылка) "
question_2 = "Сколько времени готовы уделять работе?"
question_3 = "Был ли опыт в скаме? Если да, то какой?"
# __________________________Отображение вопросов у админа__________________________
admin_question_1 = "От куда пришел чел"
admin_question_2 = "Время на ворк"
admin_question_3 = "Опыт в скаме"
# _________________________________________________________


# __________________________Действие при старте бота__________________________
async def on_startup(_):
    print("Bot Started")
# _________________________________________________________


# __________________________Действие с БД__________________________
class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()


        print("Всё кайф")

    def add_user(self, ID, username):
        with self.connection:
            try:
                self.cursor.execute("INSERT INTO 'user' VALUES (?, ?, ?, ?, ?)", (ID, "null", "null", "null", username))
            except: pass

    def add_client(self, ID):
        with self.connection:
            try:
                self.cursor.execute("INSERT INTO 'client' VALUES (?)", (ID,))
            except: pass

    def update_user_data(self, ID, a1, a2, a3):
        with self.connection:
            self.cursor.execute("UPDATE 'user' SET answer1 = ?, answer2 = ?, answer3 = ? WHERE user_id = ?", (a1, a2, a3, ID))

    def get_user_data(self, ID):
        with self.connection:
            return self.cursor.execute("SELECT * FROM 'user' WHERE user_id = ?", (ID,)).fetchmany()[0]

    def delete_zayavka(self, ID):
        with self.connection:
            return self.cursor.execute("DELETE FROM 'user' WHERE user_id = ?", (ID,))

    def client_exists(self, ID):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'user' WHERE user_id = ?", (ID,)).fetchmany(1)
            if not bool(len(result)):
                return False
            else: return True

    def confirmed_user(self, ID):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'client' WHERE user_id = ?", (ID,)).fetchmany(1)
            if not bool(len(result)):
                return False
            else: return True
# _________________________________________________________

# __________________________Кнопки__________________________
cb = CallbackData("fabnum", "action")

main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(InlineKeyboardButton(text='Подать заявку', callback_data=cb.new(action='start_answer')))

send_menu = InlineKeyboardMarkup(row_width=2)
send_menu.add(InlineKeyboardButton(text="Отправить💬", callback_data=cb.new(action="send")),
              InlineKeyboardButton(text="Заполнить заново", callback_data=cb.new(action='application')))


def admin_menu(ID):
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(InlineKeyboardButton(text="Принять✅", callback_data=f"#y{str(ID)}"),
             InlineKeyboardButton(text="Отклонить❌", callback_data=f'#n{str(ID)}'))
    return menu
# _________________________________________________________

# __________________________Подключаем БД__________________________
db = Database("../../bot/data.db")
# _________________________________________________________


class get_answer(StatesGroup):
    answer1 = State()
    answer2 = State()
    answer3 = State()


# ____________________________________________________
# @dp.message_handlers(commands=["start"])
async def command_start(message: types.Message):  # Действие при /start
    if message.from_user.username is not None:
        if db.confirmed_user(message.from_user.id):
            await bot.send_message(message.from_user.id, "❇️ Вы уже приняты 👍", reply_markup=keyboard.mainmenu)

            await call.answer(message.answer)
        else:
            if db.client_exists(message.from_user.id):
                await bot.send_message(message.from_user.id, "Вы уже подавали заявку ❌")
            else:
                await bot.send_message(message.from_user.id,
                                       "⭐️Добро пожаловать⭐️\n \n🔥Тебя приветствует PALADINS TEAM🔥 \n \n✅Подавай заявку✅",  # Приветственное сообщение
                                       reply_markup=main_menu)
    else:
        await bot.send_message(message.from_user.id, "У вас не установлен <b>username</b>(имя пользователя)\n\nУстановите его и напишите /start", parse_mode=types.ParseMode.HTML)

# @dp.callback_query_handlers(cb.filter(action=["send", "application"]), state="*")
async def send_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["action"]
    current_state = await state.get_state()
    if current_state is None:
        return
    if action == "send":
        await bot.send_message(admin_id, f"Поступила новая заявка от @{str(db.get_user_data(call.from_user.id)[4])}\n"
                                         f"{admin_question_1}: <b>{str(db.get_user_data(call.from_user.id)[1])}</b>\n"
                                         f"{admin_question_2}: <b>{str(db.get_user_data(call.from_user.id)[2])}</b>\n"
                                         f"{admin_question_3}: <b>{str(db.get_user_data(call.from_user.id)[3])}</b>", parse_mode=types.ParseMode.HTML, reply_markup=admin_menu(call.from_user.id))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Заявка отправлена, ожидайте")
        await state.finish()
    if action == "application":
        db.delete_zayavka(call.from_user.id)
        await state.finish()
        await command_start(call)
    await call.answer()


# @dp.callback_query_handler(text_contains="#")
async def access(call: types.CallbackQuery):  # Обработка заявки
    temp = [call.data[1:2], call.data[2:]]
    if temp[0] == "y":
        db.add_client(temp[1])
        db.delete_zayavka(temp[1])
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы приняли заявку✅")
        await bot.send_message(temp[1], f'Поздравляю, вы приняты в нашу команду, удачной работы⚡️ ✅\n \n'
                                        f'🔖 Ссылка для вступления в чат: {chat_link} \n \n'
                                        f'❗️ <b>ХОРОШИХ МАМОНТОВ ❗️</b>', reply_markup=keyboard.mainmenu,
                               disable_web_page_preview=True, parse_mode=types.ParseMode.HTML)


    elif temp[0] == "n":
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы отклонили заявку❌")
        await bot.send_message(temp[1], 'Извините, вы нам не подходите ❌')

    await call.answer()

async def keyboard_handler(message: types.message):
    try:
        match message.text:
            case "Выплаты💸":
                await message.reply('Выплаты: https://t.me/win1telegaaa')
            case "Чат💬":
                await message.reply('Чатик: https://t.me/+BI-3nBV-yn8xODk6')
            case "⚡️ЗАРЯД⚡️":
                await message.reply('⚡️⚡️⚡️ЗАРЯД НА ЕБНУТЫЙ СКАМ⚡️⚡️⚡️️')
            case "📚Мануалы":
                await message.reply('💸Мануалы: https://t.me/+ChWPHcqwK_AxMzQy')
            case "💼О проекте":
                await  message.reply("""ℹ️ Информация о проекте:
📆 Мы открылись: 14.08.2023

┏ 💰 Выплаты:
┣Прямики:80%
┣Клауд:60%
┗Шантаж дп:60%""")
            case _:
                pass

    except Exception as e:
        print(e)

async def command_team(message: types.Message):  # Действие при /team
                await bot.send_message(message.chat.id,
                                       """<u><b>ПЕРСОНАЛ ГРУППЫ</b></u>
👑 <b>Основатель</b>
 └ <a href="https://t.me/kristiii772">@kristiii772</a> » ТС

⚜️ <b>Соучредитель</b>
 └ <a href="https://t.me/n1tex">@n1tex</a> » Кодер

👮🏼 <b>Админ</b>
 ├ <a href="https://t.me/efremoon">@efremoon</a> » тп локер
 └ <a href="https://t.me/rasipuha">@rasipuha</a> » Гарант""", parse_mode=types.ParseMode.HTML)

async def command_card(message: types.Message):  # Действие при /card
                await bot.send_message(message.chat.id,
                                       """<b>🇺🇦Укр  (Моно банк):</b> 
<code>5375414118127207</code>
Ксенія Єпанова
(от 600 грн)
<b>🇷🇺РФ (Промсвязьбанк):</b> 
<code>5203738029970372</code>
Чуркулов Кирилл В.
(от 1.500 руб)
<b>🇰🇿КЗ (kaspiGold):</b> 
<code>4400430201189336</code>
Иван З.
(от 10.000 теньге)""", parse_mode=types.ParseMode.HTML)


async def command_mute(message):
    global comment
    name1 = message.from_user.get_mention(as_html=True)
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть ответом на сообщение!")
        return
    try:
        muteint = int(message.text.split()[1])
        mutetype = message.text.split()[2]
        comment = " ".join(message.text.split()[3:])
    except aiogram.utils.exceptions.ChatAdminRequired:
        await message.reply(f'''Нельзя дать мут администратору.''')
    except aiogram.utils.exceptions.CantRestrictChatOwner:
        await message.reply(f'''Нельзя дать мут основателю.''')

    except IndexError:
        await message.reply('Не хватает аргументов!\nПример:\n`/мут 1 ч причина`')
        return
    if mutetype == "ч" or mutetype == "часов" or mutetype == "час":
        dt = datetime.datetime.now() + timedelta(hours=muteint)
        timestamp = dt.timestamp()
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                       types.ChatPermissions(False), until_date=timestamp)
        await message.reply(
            f' | <b>Решение было принято:</b> {name1}\n | <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰ | <b>Срок наказания:</b> {muteint} {mutetype}\n | <b>Причина:</b> {comment}',
            parse_mode='html')
    elif mutetype == "м" or mutetype == "минут" or mutetype == "минуты":
        dt = datetime.datetime.now() + timedelta(minutes=muteint)
        timestamp = dt.timestamp()
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                       types.ChatPermissions(False), until_date=timestamp)
        await message.reply(
            f' | <b>Решение было принято:</b> {name1}\n | <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰ | <b>Срок наказания:</b> {muteint} {mutetype}\n | <b>Причина:</b> {comment}',
            parse_mode='html')
    elif mutetype == "д" or mutetype == "дней" or mutetype == "день":
        dt = datetime.datetime.now() + datetime.timedelta(days=muteint)
        timestamp = dt.timestamp()
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                       types.ChatPermissions(False), until_date=timestamp)
        await message.reply(
            f' | <b>Решение было принято:</b> {name1}\n | <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰ | <b>Срок наказания:</b> {muteint} {mutetype}\n | <b>Причина:</b> {comment}',
            parse_mode='html')

async def command_unmute(message: types.Message):
    try:
        if not message.reply_to_message:
            await message.reply(f'''Эта команда должна быть ответом на сообщение!''')
            return
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        await bot.send_message(message.chat.id, f'''✅ <a href='tg://user?id={message.reply_to_message.from_user.id}'>{message.reply_to_message.from_user.full_name}</a> больше не в муте.''', parse_mode='html')



async def start_state(call: types.CallbackQuery, callback_data: dict):  # Первый вопрос
    action = callback_data["action"]
    if action == "start_answer":
        db.add_user(call.from_user.id, call.from_user.username)
        await bot.send_message(call.from_user.id, f"Ответьте на несколько вопросов:\n1) <b>{question_1}</b>", parse_mode=types.ParseMode.HTML)
        await get_answer.answer1.set()


# @dp.message_handlers(state=get_answer.answer1)
async def answer1(message: types.Message, state: FSMContext):  # Второй вопрос
    async with state.proxy() as data:
        data["answer1"] = message.text
    await bot.send_message(message.from_user.id, f'2) <b>{question_2}</b>', parse_mode=types.ParseMode.HTML)
    await get_answer.next()


# @dp.message_handlers(state=get_answer.answer2)
async def answer2(message: types.Message, state: FSMContext):  # Третий вопрос
    async with state.proxy() as data:
        data["answer2"] = message.text
    await bot.send_message(message.from_user.id, f'3) <b>{question_3}</b>', parse_mode=types.ParseMode.HTML)
    await get_answer.next()


# @dp.message_handlers(state=get_answer.answer3)
async def answer3(message: types.Message, state: FSMContext):  # Отображение ответов на вопросы
    async with state.proxy() as data:
        data["answer3"] = message.text
    await bot.send_message(message.from_user.id, f'Ответы на наши вопросы:\n\n'
                                                 f'1) <b>{data["answer1"]}</b>\n'
                                                 f'2) <b>{data["answer2"]}</b>\n'
                                                 f'3) <b>{data["answer3"]}</b>', parse_mode=types.ParseMode.HTML, reply_markup=send_menu)
    db.update_user_data(message.from_user.id, data["answer1"], data["answer2"], data["answer3"])
# _________________________________________________________


# __________________________Обработка всех событий__________________________
def register_handlers_client(dp: Dispatcher):
    dp.register_callback_query_handler(send_state, cb.filter(action=["send", "application"]), state="*")
    dp.message_handler(commands=['мут', 'mute'], commands_prefix='./', is_chat_admin=True)
    dp.message_handler(commands=['размут', 'unmute'], commands_prefix='/!.', is_chat_admin=True)
    dp.register_message_handler(command_start, commands=["start"])
    dp.register_message_handler(command_team, commands=["team"])
    dp.register_message_handler(command_card, commands=["card"])
    dp.register_message_handler(command_mute, commands=['мут', 'mute'])
    dp.register_message_handler(command_unmute, commands=['анмут', 'unmute'])
    dp.register_callback_query_handler(access, text_contains="#")
    dp.register_callback_query_handler(start_state, cb.filter(action=["start_answer"]))
    dp.register_message_handler(answer1, state=get_answer.answer1)
    dp.register_message_handler(answer2, state=get_answer.answer2)
    dp.register_message_handler(answer3, state=get_answer.answer3)
    dp.register_message_handler(keyboard_handler, state='*')
# _________________________________________________________


register_handlers_client(dp)  # Запуск обработки событий


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)

