start_text = 'DotAIBuffBot Р·Р°РїСѓС‰РµРЅ.'
gsi_config_caption = 'РџРѕР»РѕР¶Рё С„Р°Р№Р» РІ РїР°РїРєСѓ Dota 2 gamestate_integration.'
gsi_config_info = '''GSI-РєРѕРЅС„РёРі СЃРІСЏР·С‹РІР°РµС‚ Dota 2 СЃ Р»РѕРєР°Р»СЊРЅС‹Рј СЃРµСЂРІРёСЃРѕРј DotAIBuffBot. РРіСЂР° РѕС‚РїСЂР°РІР»СЏРµС‚ С‡РµСЂРµР· РЅРµРіРѕ РґР°РЅРЅС‹Рµ РјР°С‚С‡Р°, Р° Р±РѕС‚ С„РѕСЂРјРёСЂСѓРµС‚ СЂРµРєРѕРјРµРЅРґР°С†РёРё.

1. РЎРєР°С‡Р°Р№С‚Рµ config С‡РµСЂРµР· РєРЅРѕРїРєСѓ В«РџРѕР»СѓС‡РёС‚СЊ GSI configВ».
2. РџРѕР»РѕР¶РёС‚Рµ С„Р°Р№Р» РІ РїР°РїРєСѓ:

Windows:
...\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg\\gamestate_integration\\

Linux:
~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration/

3. Р’ Steam РѕС‚РєСЂРѕР№С‚Рµ СЃРІРѕР№СЃС‚РІР° Dota 2 Рё РґРѕР±Р°РІСЊС‚Рµ РІ Launch Options:
-gamestateintegration

4. РџРµСЂРµР·Р°РїСѓСЃС‚РёС‚Рµ Dota 2.

DotAIBuffBot РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ Р·Р°РїСѓС‰РµРЅ РЅР° С‚РѕРј Р¶Рµ РєРѕРјРїСЊСЋС‚РµСЂРµ, С‡С‚Рѕ Рё Dota 2.'''
snapshot_not_received = 'Р”Р°РЅРЅС‹Рµ С‚РµРєСѓС‰РµРіРѕ РјР°С‚С‡Р° РµС‰Рµ РЅРµ РїРѕР»СѓС‡РµРЅС‹.'
snapshot_title = 'РўРµРєСѓС‰РµРµ СЃРѕСЃС‚РѕСЏРЅРёРµ РјР°С‚С‡Р°'
match_label = 'РњР°С‚С‡'
game_state_label = 'РЎРѕСЃС‚РѕСЏРЅРёРµ'
time_label = 'Р’СЂРµРјСЏ'
seconds_label = 'СЃРµРє'
score_label = 'РЎС‡РµС‚'
hero_label = 'Р“РµСЂРѕР№'
level_label = 'РЈСЂРѕРІРµРЅСЊ'
hp_label = 'HP'
mana_label = 'Mana'
gold_label = 'Gold'
kda_label = 'KDA'
abilities_label = 'Abilities'
ability_level_label = 'СѓСЂРѕРІРµРЅСЊ'
cooldown_label = 'РїРµСЂРµР·Р°СЂСЏРґРєР°'
items_label = 'Items'
radiant_label = 'Radiant'
dire_label = 'Dire'
language_changed = 'РЇР·С‹Рє РёР·РјРµРЅРµРЅ.'
macro_advice_title = 'РњР°РєСЂРѕРіРµР№РјРёРЅРі'
build_advice_title = 'РЎР±РѕСЂРєР°'
micro_advice_title = 'РњРёРєСЂРѕРіРµР№РјРёРЅРі: РїСЂРёРѕСЂРёС‚РµС‚ СЃРµР№С‡Р°СЃ'
advice_request_failed = 'РќРµ СѓРґР°Р»РѕСЃСЊ РїРѕР»СѓС‡РёС‚СЊ СЂРµРєРѕРјРµРЅРґР°С†РёСЋ РР. РџРѕРїСЂРѕР±СѓР№С‚Рµ РїРѕР·Р¶Рµ.'



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
    return f'РЎР»РµРґСѓСЋС‰СѓСЋ СЂРµРєРѕРјРµРЅРґР°С†РёСЋ РјРѕР¶РЅРѕ Р·Р°РїСЂРѕСЃРёС‚СЊ С‡РµСЂРµР· {remaining_time} СЃРµРє.'


def match_started(match_id: int):
    """Return match started notification."""
    return f'РњР°С‚С‡ {match_id} РЅР°С‡Р°Р»СЃСЏ.\nID РјР°С‚С‡Р°: {match_id}'


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
