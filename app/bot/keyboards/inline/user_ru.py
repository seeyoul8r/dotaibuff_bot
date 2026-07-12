from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


getGsiConfigBtn = InlineKeyboardButton(text='Получить GSI config', callback_data='get_gsi_config')
whatIsGsiConfigBtn = InlineKeyboardButton(text='Что такое GSI-конфиг?', callback_data='what_is_gsi_config')
getAiAdviceBtn = InlineKeyboardButton(text='Получить рекомендацию ИИ', callback_data='get_ai_advice')
newAiAdviceBtn = InlineKeyboardButton(text='\u041d\u043e\u0432\u044b\u0439 \u0437\u0430\u043f\u0440\u043e\u0441', callback_data='get_ai_advice')
changeLanguageBtn = InlineKeyboardButton(text='English', callback_data='change_language')

mainMenu = InlineKeyboardMarkup(inline_keyboard=[
    [getGsiConfigBtn],
    [whatIsGsiConfigBtn],
    [getAiAdviceBtn],
    [changeLanguageBtn]
])

afterAdviceMenu = InlineKeyboardMarkup(inline_keyboard=[
    [newAiAdviceBtn]
])
