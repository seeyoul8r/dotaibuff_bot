# DotAIBuffBot

## Getting started

- Send `/start` to the bot to register.
- The bot shows a welcome message with a short service description and opens the main menu.
- If you send a message or press an old button before registration, the bot explains the service and asks you to use `/start`.
- Sending `/start` again opens the main menu without registering again.

## GSI config

- Send `/start` to the bot.
- Press `Get GSI config`.
- Download `gamestate_integration_dot_ai_buff_bot.cfg`.
- Put the file into the Dota 2 folder:
  `...\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration\`
- On Linux use:
  `~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration/`
- Open Dota 2 properties in Steam and add `-gamestateintegration` to Launch Options.
- Start or restart Dota 2.
- If the config was already installed before, download it again and replace the old file.
- When a match starts and the bot receives the first GSI snapshot with match id, it sends a notification.
- Press `What is GSI config?` for a short installation guide.

## AI recommendation

- Press `Get AI recommendation`.
- The bot combines accumulated match state with current OpenDota data and requests advice from AI.
- Telegram shows a temporary animated Thinking status while AI prepares the response.
- The response arrives as three messages: macro gaming, build, and the current micro gaming priority. Each message shows the match time it is based on.
- If AI does not respond, the bot reports the error.
- Each user can request advice no more than once every 3 minutes.
- If current match GSI data has not been received yet, the bot reports it without starting an AI request.
- When the match ends, the bot sends a final summary with winner, score, hero, level, KDA, and match time.

## Language

- Press `Русский` to switch the interface to Russian.
- The selected language is saved in user settings.
