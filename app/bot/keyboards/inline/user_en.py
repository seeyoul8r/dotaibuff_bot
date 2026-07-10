from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


getGsiConfigBtn = InlineKeyboardButton(text='Get GSI config', callback_data='get_gsi_config')
whatIsGsiConfigBtn = InlineKeyboardButton(text='What is GSI config?', callback_data='what_is_gsi_config')
getAiAdviceBtn = InlineKeyboardButton(text='Get AI recommendation', callback_data='get_ai_advice')
changeLanguageBtn = InlineKeyboardButton(text='Русский', callback_data='change_language')

mainMenu = InlineKeyboardMarkup(inline_keyboard=[
    [getGsiConfigBtn],
    [whatIsGsiConfigBtn],
    [getAiAdviceBtn],
    [changeLanguageBtn]
])
