from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


getGsiConfigBtn = InlineKeyboardButton(text='Get GSI config', callback_data='get_gsi_config')
whatIsGsiConfigBtn = InlineKeyboardButton(text='What is GSI config?', callback_data='what_is_gsi_config')
openGsiMenuBtn = InlineKeyboardButton(text='GSI config', callback_data='open_gsi_menu')
backToMainMenuBtn = InlineKeyboardButton(text='Back', callback_data='back_to_main_menu')
getAiAdviceBtn = InlineKeyboardButton(text='📞 Get AI advice', callback_data='get_ai_advice')
newAiAdviceBtn = InlineKeyboardButton(text='📞 Get AI advice', callback_data='get_ai_advice')
changeLanguageBtn = InlineKeyboardButton(text='Lang: RU', callback_data='change_language')

mainMenu = InlineKeyboardMarkup(inline_keyboard=[
    [openGsiMenuBtn],
    [changeLanguageBtn]
])

gsiMenu = InlineKeyboardMarkup(inline_keyboard=[
    [getGsiConfigBtn],
    [whatIsGsiConfigBtn],
    [backToMainMenuBtn]
])

afterAdviceMenu = InlineKeyboardMarkup(inline_keyboard=[
    [newAiAdviceBtn]
])

matchStartedMenu = InlineKeyboardMarkup(inline_keyboard=[
    [getAiAdviceBtn]
])
