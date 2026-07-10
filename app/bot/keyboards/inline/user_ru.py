from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


getGsiConfigBtn = InlineKeyboardButton(text='Получить GSI config', callback_data='get_gsi_config')
whatIsGsiConfigBtn = InlineKeyboardButton(text='Что такое GSI-конфиг?', callback_data='what_is_gsi_config')
getAiAdviceBtn = InlineKeyboardButton(text='Получить рекомендацию ИИ', callback_data='get_ai_advice')
changeLanguageBtn = InlineKeyboardButton(text='English', callback_data='change_language')

mainMenu = InlineKeyboardMarkup(inline_keyboard=[
    [getGsiConfigBtn],
    [whatIsGsiConfigBtn],
    [getAiAdviceBtn],
    [changeLanguageBtn]
])
