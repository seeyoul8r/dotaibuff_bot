start_text = 'DotAIBuffBot запущен.'
gsi_config_caption = 'Положи файл в папку Dota 2 gamestate_integration.'
gsi_config_info = '''GSI-конфиг связывает Dota 2 с сервисом DotAIBuffBot. Игра отправляет через него данные матча, а бот формирует рекомендации.

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
abilities_label = 'Способности'
ability_level_label = 'уровень'
cooldown_label = 'перезарядка'
items_label = 'Предметы'
radiant_label = 'Radiant'
dire_label = 'Dire'
language_changed = 'Язык изменен.'
macro_advice_title = 'Макрогейминг'
build_advice_title = 'Сборка'
micro_advice_title = 'Микрогейминг: приоритет сейчас'
advice_request_failed = 'Не удалось получить рекомендацию ИИ. Попробуйте позже.'


def format_match_time(clock_time: int | None):
    """Return match time as MM:SS."""
    if clock_time is None:
        return 'неизвестно'
    minutes = max(clock_time, 0) // 60
    seconds = max(clock_time, 0) % 60
    return f'{minutes}:{seconds:02d}'


def advice_actual_at(clock_time: int | None):
    """Return advice match time header."""
    return f'Актуально на {format_match_time(clock_time)} матча'


def advice_on_cooldown(remaining_time: int):
    """Return advice cooldown message."""
    return f'Следующую рекомендацию можно запросить через {remaining_time} сек.'


def match_started(match_id: int):
    """Return match started notification."""
    return f'Матч {match_id} начался.\nID матча: {match_id}'


def match_finished(match_state: dict):
    """Return match finished summary."""
    player = match_state['player']
    hero = match_state['hero']
    return (
        f'Матч завершен.\n'
        f'ID матча: {match_state.get("match_id")}\n'
        f'Победитель: {match_state.get("win_team")}\n'
        f'Счет: Radiant {match_state.get("radiant_score")} / Dire {match_state.get("dire_score")}\n'
        f'Герой: {hero.get("name")}\n'
        f'Уровень: {hero.get("level")}\n'
        f'KDA: {player.get("kills")} / {player.get("deaths")} / {player.get("assists")}\n'
        f'Время: {format_match_time(match_state.get("clock_time"))}'
    )
