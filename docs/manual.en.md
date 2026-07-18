# DotAIBuffBot

## Getting started

- Send `/start` to the bot to register.
- The bot shows a welcome message with a short service description and opens the main menu.
- If you send a message or press an old button before registration, the bot explains the service and asks you to use `/start`.
- Sending `/start` again opens the main menu without registering again.

## GSI config

- Send `/start` to the bot.
- Press `GSI config`.
- Press `Get GSI config` inside the GSI submenu.
- Download `gamestate_integration_dot_ai_buff_bot.cfg`.
- Put the file into the Dota 2 folder:
  `...\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration\`
- On Linux use:
  `~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration/`
- Open Dota 2 properties in Steam and add `-gamestateintegration` to Launch Options.
- Start or restart Dota 2.
- If the config was already installed before, download it again and replace the old file.
- When a match starts and the bot receives the first GSI snapshot with match id, it sends a notification with the `♿️ Where are enemies?` and `📦 Get AI advice` buttons.
- Press `GSI config` in the main menu to open GSI actions.
- Press `Get GSI config` inside the GSI submenu only when you need to download or replace the config file.
- Press `What is GSI config?` inside the GSI submenu for a short installation guide.
- Press `Back` to return to the main menu.

## AI recommendation

- Press `📦 Get AI advice` in the match start notification.
- The bot combines accumulated match state with current OpenDota data and requests advice from AI.
- After the full enemy roster is known, the recommendation uses where and when enemies were last seen on the minimap.
- Telegram shows a temporary animated Thinking status while AI prepares the response.
- The response arrives as one message with macro gaming, build, and the current micro gaming priority. It shows the match time it is based on.
- At the end of the response, the bot shows when the next request is available and adds the `♿️ Where are enemies?` and `📦 Get AI advice` buttons.
- If AI does not respond, the bot reports the error.
- Each user can request advice no more than once every 3 minutes.
- If current match GSI data has not been received yet, the bot reports it without starting an AI request.
- Press `♿️ Where are enemies?` to get a separate message with match time and the `Enemy map info` list.
- The enemy block shows English map area names, such as `Radiant Triangle`, `Dire Safe Lane`, or `Bot Roshan Pit`.
- If an enemy has not been seen on the minimap yet, the bot shows `Not seen yet`; if coordinates are too far from the nearest configured zone, the bot shows `Unknown area`.
- When the match ends, the bot sends a final summary with winner, score, hero, level, KDA, and match time. After that, advice for the finished match cannot be requested.

## Language

- Press `Lang: RU` to switch the interface to Russian.
- The selected language is saved in user settings.
