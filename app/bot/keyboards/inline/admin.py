from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


manageUserBtn = InlineKeyboardButton(text='Manage User', callback_data='admin_manage_user')
userListBtn = InlineKeyboardButton(text='Userlist', callback_data='admin_users_list')
sendAllBtn = InlineKeyboardButton(text='Send all', callback_data='admin_send_all')
updateDbBtn = InlineKeyboardButton(text='Update DB', callback_data='admin_update_db')
updateDotaDataBtn = InlineKeyboardButton(text='Update Dota data', callback_data='update_dota_data')
setAdviceCooldownBtn = InlineKeyboardButton(text='Set advice cooldown', callback_data='admin_set_advice_cooldown')
errorLogBtn = InlineKeyboardButton(text='Error log', callback_data='admin_show_errors')
cleanErrorBtn = InlineKeyboardButton(text='Clean log', callback_data='admin_clean_errors')

adminMainKb = InlineKeyboardMarkup(inline_keyboard=[
    [manageUserBtn, userListBtn],
    [sendAllBtn, updateDbBtn],
    [updateDotaDataBtn, setAdviceCooldownBtn],
    [errorLogBtn, cleanErrorBtn]
])

adminCancelBtn = InlineKeyboardButton(text='Cancel input', callback_data='cancel_input')
adminCancelKb = InlineKeyboardMarkup(inline_keyboard=[[adminCancelBtn]])
