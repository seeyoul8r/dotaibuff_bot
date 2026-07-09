start_text = 'DotAIBuffBot started.'
gsi_config_caption = 'Put the file into the Dota 2 gamestate_integration folder.'
snapshot_not_received = 'GSI snapshot has not been received yet.'
snapshot_title = 'Current snapshot'
match_label = 'Match'
time_label = 'Time'
seconds_label = 'sec'
hero_label = 'Hero'
level_label = 'Level'
gold_label = 'Gold'
abilities_label = 'Abilities'
items_label = 'Items'
language_changed = 'Language changed.'


def match_started(match_id: int):
    """Return match started notification."""
    return f'Match {match_id} has started.\nMatch ID: {match_id}'
