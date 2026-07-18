start_text = 'DotAIBuffBot started.'
welcome = '''Welcome to DotAIBuffBot!

The service receives the current Dota 2 match state through GSI. On request, the bot shows enemy map info, and AI analyzes the accumulated data to send three recommendations: macro gaming, a build, and the current micro gaming priority.

Get and install your personal GSI config from the menu below to begin.'''
unregistered = '''To use DotAIBuffBot, register first with the /start command.

The service receives current match data through GSI and provides enemy map info separately from AI recommendations for macro gaming, builds, and micro gaming.'''
gsi_config_caption = 'Put the file into the Dota 2 gamestate_integration folder.'
gsi_config_info = '''A GSI config connects Dota 2 to the local DotAIBuffBot service. The game sends match data through it, and the bot prepares recommendations.

1. Download the config with the Get GSI config button.
2. Put the file into:

Windows:
...\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg\\gamestate_integration\\

Linux:
~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration/

3. Restart Dota 2.'''
snapshot_not_received = 'Current match data has not been received yet.'
snapshot_title = 'Current match state'
match_label = 'Match'
game_state_label = 'State'
time_label = 'Time'
seconds_label = 'sec'
score_label = 'Score'
hero_label = 'Hero'
level_label = 'Level'
hp_label = 'HP'
mana_label = 'Mana'
gold_label = 'Gold'
kda_label = 'KDA'
abilities_label = 'Abilities'
ability_level_label = 'level'
cooldown_label = 'cooldown'
items_label = 'Items'
radiant_label = 'Radiant'
dire_label = 'Dire'
language_changed = 'Language changed.'
enemy_map_info_title = 'Enemy map info'
enemy_map_info_header = 'Hero | Last seen | Time'
enemy_not_seen_yet = 'Not seen yet'
enemy_unknown_area = 'Unknown area'
enemy_no_seen_time = '-'
macro_advice_title = 'Macro gaming'
build_advice_title = 'Build'
micro_advice_title = 'Micro gaming: current priority'
advice_request_failed = 'Failed to get AI advice. Please try again later.'


def format_match_time(clock_time: int | None):
    """Return match time as MM:SS."""
    if clock_time is None:
        return 'unknown'
    minutes = max(clock_time, 0) // 60
    seconds = max(clock_time, 0) % 60
    return f'{minutes}:{seconds:02d}'


def advice_actual_at(clock_time: int | None):
    """Return advice match time header."""
    return f'Actual at {format_match_time(clock_time)} of the match'


def advice_on_cooldown(remaining_time: int):
    """Return advice cooldown message."""
    return f'You can request the next recommendation in {remaining_time} sec.'


def next_advice_available(cooldown_period: int):
    """Return next advice availability message."""
    return f'You can make the next request in {cooldown_period} sec.'


def enemy_seen_time(visible: bool, seen_seconds_ago: int | None):
    """Return enemy last seen time text."""
    if visible:
        return 'now'
    return f'{seen_seconds_ago} sec ago'


def match_started(match_id: int):
    """Return match started notification."""
    return f'Match started. ID: {match_id}'


def match_finished(match_state: dict):
    """Return match finished summary."""
    player = match_state['player']
    hero = match_state['hero']
    return (
        f'Match finished.\n'
        f'Match ID: {match_state.get("match_id")}\n'
        f'Winner: {match_state.get("win_team")}\n'
        f'Score: Radiant {match_state.get("radiant_score")} / Dire {match_state.get("dire_score")}\n'
        f'Hero: {hero.get("name")}\n'
        f'Level: {hero.get("level")}\n'
        f'KDA: {player.get("kills")} / {player.get("deaths")} / {player.get("assists")}\n'
        f'Time: {format_match_time(match_state.get("clock_time"))}'
    )
