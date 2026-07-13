from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


getGsiConfigBtn = InlineKeyboardButton(text='\u041f\u043e\u043b\u0443\u0447\u0438\u0442\u044c GSI config', callback_data='get_gsi_config')
whatIsGsiConfigBtn = InlineKeyboardButton(text='\u0427\u0442\u043e \u0442\u0430\u043a\u043e\u0435 GSI-\u043a\u043e\u043d\u0444\u0438\u0433?', callback_data='what_is_gsi_config')
openGsiMenuBtn = InlineKeyboardButton(text='GSI-\u043a\u043e\u043d\u0444\u0438\u0433', callback_data='open_gsi_menu')
backToMainMenuBtn = InlineKeyboardButton(text='\u041d\u0430\u0437\u0430\u0434', callback_data='back_to_main_menu')
getAiAdviceBtn = InlineKeyboardButton(text='📞 Получить совет ИИ', callback_data='get_ai_advice')
newAiAdviceBtn = InlineKeyboardButton(text='📞 Получить совет ИИ', callback_data='get_ai_advice')
changeLanguageBtn = InlineKeyboardButton(text='Lang: EN', callback_data='change_language')

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
