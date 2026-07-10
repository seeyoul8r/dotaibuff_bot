start_text = 'DotAIBuffBot запущен.'
gsi_config_caption = 'Положи файл в папку Dota 2 gamestate_integration.'
gsi_config_info = '''GSI-конфиг связывает Dota 2 с локальным сервисом DotAIBuffBot. Игра отправляет через него данные матча, а бот формирует рекомендации.

1. Скачайте config через кнопку «Получить GSI config».
2. Положите файл в папку:

Windows:
...\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg\\gamestate_integration\\

Linux:
~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration/

3. В Steam откройте свойства Dota 2 и добавьте в Launch Options:
-gamestateintegration

4. Перезапустите Dota 2.

DotAIBuffBot должен быть запущен на том же компьютере, что и Dota 2.'''
snapshot_not_received = 'Данные текущего матча еще не получены.'
snapshot_title = 'Текущее состояние матча'
match_label = 'Матч'
game_state_label = 'Состояние'
time_label = 'Время'
seconds_label = 'сек'
score_label = 'Счет'
hero_label = 'Герой'
level_label = 'Уровень'
hp_label = 'HP'
mana_label = 'Mana'
gold_label = 'Gold'
kda_label = 'KDA'
abilities_label = 'Abilities'
ability_level_label = 'уровень'
cooldown_label = 'перезарядка'
items_label = 'Items'
radiant_label = 'Radiant'
dire_label = 'Dire'
language_changed = 'Язык изменен.'
macro_advice_title = 'Макрогейминг'
build_advice_title = 'Сборка'
micro_advice_title = 'Микрогейминг: приоритет сейчас'
advice_request_failed = 'Не удалось получить рекомендацию ИИ. Попробуйте позже.'


def advice_on_cooldown(remaining_time: int):
    """Return advice cooldown message."""
    return f'Следующую рекомендацию можно запросить через {remaining_time} сек.'


def match_started(match_id: int):
    """Return match started notification."""
    return f'Матч {match_id} начался.\nID матча: {match_id}'
