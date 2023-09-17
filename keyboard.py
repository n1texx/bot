from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

mainmenu_Chat = KeyboardButton('⚡️ЗАРЯД⚡️')
mainmenu_Dengi = KeyboardButton('Чат💬')
mainmenu_Zaryad = KeyboardButton('Выплаты💸')
mainmenu_Manual = KeyboardButton('📚Мануалы')
mainmenu_Project = KeyboardButton('💼О проекте')

mainmenu = ReplyKeyboardMarkup(resize_keyboard = True).add(mainmenu_Dengi, mainmenu_Chat, mainmenu_Zaryad, mainmenu_Manual, mainmenu_Project)
