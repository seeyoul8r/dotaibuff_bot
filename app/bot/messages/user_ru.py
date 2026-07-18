start_text = 'DotAIBuffBot запущен.'
welcome = '''Добро пожаловать в DotAIBuffBot!

Сервис получает состояние текущего матча из Dota 2 через GSI. По вашему запросу бот показывает информацию о врагах на карте, а ИИ анализирует накопленные данные и присылает три рекомендации: макрогейминг, сборку и текущий приоритет по микрогеймингу.

Получите и установите персональный GSI config через меню ниже, чтобы начать.'''
unregistered = '''Чтобы использовать DotAIBuffBot, сначала зарегистрируйтесь командой /start.

Сервис получает данные текущего матча через GSI и формирует информацию о врагах на карте отдельно от рекомендаций ИИ по макрогеймингу, сборке и микрогеймингу.'''
gsi_config_caption = 'Положи файл в папку Dota 2 gamestate_integration.'
gsi_config_info = '''GSI-конфиг связывает Dota 2 с сервисом DotAIBuffBot. Игра отправляет через него данные матча, а бот формирует рекомендации.

1. Скачайте config через кнопку «Получить GSI config».
2. Положите файл в папку:

Windows:
...\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg\\gamestate_integration\\

Linux:
~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration/

3. Перезапустите Dota 2.'''
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
enemy_map_info_title = 'Враги на карте'
enemy_map_info_header = 'Герой | Где видели | Когда'
enemy_not_seen_yet = 'Not seen yet'
enemy_unknown_area = 'Unknown area'
enemy_no_seen_time = '-'
map_location_names = {
    'unknown': 'неизвестно',
    'radiant_fountain': 'фонтан Radiant',
    'radiant_throne': 'трон Radiant',
    'radiant_safelane_t3': 'T3 Radiant на легкой',
    'radiant_safelane_t2': 'T2 Radiant на легкой',
    'radiant_safelane_t1': 'T1 Radiant на легкой',
    'radiant_safelane_jungle': 'лес Radiant у легкой',
    'radiant_safelane_forest': 'лес Radiant у легкой',
    'radiant_lotus_pool': 'лотос Radiant',
    'radiant_tormentor': 'терзатель Radiant',
    'radiant_twin_gate': 'портал Radiant',
    'radiant_mid_t3': 'T3 Radiant на миде',
    'radiant_mid_t2': 'T2 Radiant на миде',
    'radiant_mid_t1': 'T1 Radiant на миде',
    'bot_river': 'нижняя река',
    'bot_roshan_pit': 'нижний Рошан-пит',
    'dire_secret_shop': 'потайная лавка Dire',
    'mid_river': 'река на миде',
    'dire_mid_t1': 'T1 Dire на миде',
    'top_river': 'верхняя река',
    'top_roshan_pit': 'верхний Рошан-пит',
    'radiant_secret_shop': 'потайная лавка Radiant',
    'dire_mid_t2': 'T2 Dire на миде',
    'dire_mid_t3': 'T3 Dire на миде',
    'dire_throne': 'трон Dire',
    'dire_fountain': 'фонтан Dire',
    'radiant_triangle': 'треугольник Radiant',
    'radiant_offlane_t2': 'T2 Radiant на сложной',
    'radiant_offlane_t1': 'T1 Radiant на сложной',
    'radiant_wisdom_rune': 'руна опыта Radiant',
    'radiant_offlane_jungle': 'лес Radiant у сложной',
    'radiant_offlane_bridge': 'мост на сложной Radiant',
    'dire_lotus_pool': 'лотос Dire',
    'dire_tormentor': 'терзатель Dire',
    'dire_twin_gate': 'портал Dire',
    'dire_safelane_jungle': 'лес Dire у легкой',
    'dire_safelane_t3': 'T3 Dire на легкой',
    'dire_safelane_t2': 'T2 Dire на легкой',
    'dire_safelane_forest': 'лес Dire у легкой',
    'dire_offlane_t1': 'T1 Dire на сложной',
    'dire_offlane_t2': 'T2 Dire на сложной',
    'dire_wisdom_rune': 'руна опыта Dire',
    'dire_offlane_jungle': 'лес Dire у сложной',
    'dire_offlane_bridge': 'мост на сложной Dire',
    'dire_triangle': 'треугольник Dire'
}
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


def next_advice_available(cooldown_period: int):
    """Return next advice availability message."""
    return (
        f'\u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0441\u0434\u0435\u043b\u0430\u0442\u044c '
        f'\u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0437\u0430\u043f\u0440\u043e\u0441 '
        f'\u0447\u0435\u0440\u0435\u0437 {cooldown_period} \u0441\u0435\u043a.'
    )


def enemy_seen_time(visible: bool, seen_seconds_ago: int | None):
    """Return enemy last seen time text."""
    if visible:
        return 'сейчас'
    return f'{seen_seconds_ago} сек назад'


def match_started(match_id: int):
    """Return match started notification."""
    return f'Матч начался. ID: {match_id}'


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
