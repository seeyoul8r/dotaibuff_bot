start_text = 'DotAIBuffBot запущен.'
gsi_config_caption = 'Положи файл в папку Dota 2 gamestate_integration.'
snapshot_not_received = 'GSI snapshot еще не получен.'
snapshot_title = 'Текущий snapshot'
match_label = 'Матч'
time_label = 'Время'
seconds_label = 'сек'
hero_label = 'Герой'
level_label = 'Уровень'
gold_label = 'Gold'
abilities_label = 'Abilities'
items_label = 'Items'
language_changed = 'Язык изменен.'


def match_started(match_id: int):
    """Return match started notification."""
    return f'Матч {match_id} начался.\nID матча: {match_id}'
