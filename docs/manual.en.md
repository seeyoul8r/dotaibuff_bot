# MarketMonitor User Guide

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Trading Rules](#2-trading-rules)
3. [Getting Started - Commands & Menus](#3-getting-started)
4. [Ticker - Manual Coin Data Request](#4-ticker-manual-coin-data-request)
5. [Signal Format - How to Read the Data](#5-signal-format-how-to-read-the-data)
6. [Screeners Section](#6-screeners-section)
   - 6.1 [Screener Settings](#61-screener-settings)
     - 6.1.1 [Screeners 1, 2: Pump & Dump](#611-screeners-1-2-pump-dump)
     - 6.1.2 [Screeners 3, 4: HourScreeners](#612-screeners-3-4-hourscreeners)
     - 6.1.3 [Screener 5: Liquidations](#613-screener-5-liquidations)
     - 6.1.4 [Screeners 6, 7: MultiScreeners](#614-screeners-6-7-multiscreeners)
     - 6.1.5 [Screeners 8, 9: Funding](#615-screeners-8-9-funding)
     - 6.1.6 [Listings and Delistings](#616-listings-and-delistings)
     - 6.1.7 [Screener Filters](#617-screener-filters)
     - 6.1.8 [Setting Parameters](#618-setting-parameters)
     - 6.1.9 [Screener Configurations](#619-screener-configurations)
   - 6.2 [Signal Counter](#62-signal-counter)
   - 6.3 [Signal Log](#63-signal-log)
   - 6.4 [Tickers](#64-tickers)
   - 6.5 [One-time Request](#65-one-time-request)
7. [Cross-Exchange Screeners](#7-cross-exchange-screeners)
   - 7.1 [InterFunding](#71-interfunding)
   - 7.2 [InterPrice](#72-interprice)
   - 7.3 [Filters & Pair Exclusion](#73-filters-pair-exclusion)
8. [API Section](#8-trading-section)
   - 8.1 [Markets Menu - Exchange Connections & API Keys](#81-markets-menu-exchange-connections-api-keys)
   - 8.2 [Trade Settings](#82-trade-configs-trading-settings)
     - 8.2.1 [Position Size](#821-position-size)
     - 8.2.2 [Order Type](#822-order-type)
     - 8.2.3 [TP - Take-Profit](#823-tp-take-profit)
     - 8.2.4 [SL - Stop-Loss](#824-sl-stop-loss)
     - 8.2.5 [Averaging](#825-averaging)
     - 8.2.6 [Position Mode](#826-position-mode)
     - 8.2.7 [Leverage](#827-leverage)
     - 8.2.8 [Position Limits](#828-position-limits)
     - 8.2.9 [Trading Configurations](#829-trading-configurations)
   - 8.3 [Autotrading - Automatic Position Opening](#83-autotrading-automatic-position-opening)
   - 8.4 [Positions - Info & Management](#84-positions-info-management)
   - 8.5 [Balance](#85-balance)
   - 8.6 [PNL - Trade History & Statistics](#86-pnl-trade-history-statistics)
   - 8.7 [Exchange Events](#87-exchange-events)
9. [Account & Subscription](#9-account-subscription)

---

<a id="1-introduction"></a>
## 1. Introduction

MarketMonitor is a bot for cryptocurrency market monitoring and futures trading. It scans 8 exchanges in real time (Binance, Bitget, Bybit, Mexc, OKX, BingX, KuCoin, Gate), filters the flow of market data according to your configured parameters, and sends trading signals. The bot can also automatically open positions based on these signals - with support for grid take-profits, averaging, auto-refills, and stop-losses.

Full-featured screeners and autotrading are available with a subscription. The **free version** only provides the **🔎 Ticker** button - a manual data request for a specific coin.

Screeners and API trading are supported on **Bybit, Binance, OKX and Bitget**. Data is updated via WebSocket streams in real time.

**If you're new to trading** - study the basics and practice manual trading first. The bot is an amplification tool, not a substitute for experience.

---

<a id="2-trading-rules"></a>
## 2. Trading Rules

Before diving into the settings, a word on what matters most. In this bot we collect real-time exchange metrics - price, OI, volume, funding, liquidations - and compare them. By applying filters (RSI, market cap, circulation), you can attempt to forecast movement: price went up but OI and volume dropped? Longs closed and took profit - consider a short. Daily RSI above 90%, hourly at 40%, funding through the roof? The coin was overbought, correction is beginning. Complex indicators (Elliott Waves, Ichimoku, MACD) often perform no better than a casino in crypto - one whale with tens of millions can ruin any analysis. Trade 3–5 highly liquid coins with a clear strategy rather than everything at once.

A few personal rules:

- Trading is a long game. No setup? Close the terminal and do something else.
- Always avoid FOMO. When it feels like everyone is making money - you're emotional, you'll make the wrong call.
- Don't average down in a flat market - you'll bloat your position pointlessly.
- Don't hedge losing positions during sharp moves - logic doesn't work at those moments, you'll act at the worst point.
- Don't hold bloated longs in weak coins. A delisting or dump will eat half your deposit.
- Don't trade off the 1-minute chart.

---

<a id="3-getting-started"></a>
## 3. Getting Started

After pressing `/start`, the main keyboard appears with three buttons:

- **🖥 Screeners** - screener settings and signal reception
- **📡 API** - API key management, trade configs, position management
- **🔎 Ticker** - manual coin data request

Main keyboard example:

| 🖥 Screeners | 📡 API | 🔎 Ticker |
|---|---|---|

Additional commands:

| Command | Description |
|---|---|
| `/start` | Open main menu |
| `/profile` | Account, subscription, referral program |

---

<a id="4-ticker-manual-coin-data-request"></a>
## 4. Ticker - Manual Coin Data Request

This is the only function available in the **free version**. After pressing the **🔎 Ticker** button, the bot will ask you to type a coin name or choose from a list of popular recent requests (up to 6 coins ranked by request frequency). Popular requests are saved between bot restarts.

Both full (`BTCUSDT`) and short (`BTC`) formats are accepted. The bot searches for the coin across all connected exchanges and returns data from the first exchange where it's found, as a card with a chart (default timeframe: 15m). The timeframe can be switched using buttons below the chart (`15min`, `1h`, `1d`). The **📊 All Exchanges** button displays data for the coin from all available exchanges at once - useful for comparing prices and funding rates.

Input examples:

```text
BTC
BTCUSDT
ETH
```

Buttons below the Ticker card:

| Button | Purpose |
|---|---|
| 15min | Rebuild chart on 15-minute timeframe |
| 1h | Rebuild chart on 1-hour timeframe |
| 1d | Rebuild chart on 1-day timeframe |
| 📊 All Exchanges | Show coin data across all exchanges |

The card format is described in detail in the next section.

---

<a id="5-signal-format-how-to-read-the-data"></a>
## 5. Signal Format - How to Read the Data

Every signal contains a consistent set of fields. Let's break them down on a real example - a pump screener signal:

---

```
🔹 [HEIUSDT] Price Pump - 10min
🟠⚫️ Bybit: 10.86% (0.13374 - 0.14826)
🔼 OI: 9.77% (1.64M - 1.80M)
🛢 Volume: 3.37% (12.36M - 12.77M)
🔄 RSI: 76.04% / 71.11% / 64.97%
📶 Funding: 0.005%
🔋 Rank: #1046 | 🔊 Signal/24H: 3
📈 Change 1h/24h: 11.55% / 14.53%
🌍 Global Vol 24h: $36.7M (V/MC: 310.8%)
🪙 Circulation: 97.76%
🧪 Innovation Zone
```

**Field breakdown:**

**Header:**
- 🔹 - screener marker (price pump, Screener 1). Full marker list - in section 6.
- [HEIUSDT](link) - clickable link to the coin's page on **Coinglass** (charts, OI, liquidations).
- "Price Pump - 10min" - signal type and period over which the move was detected.

**Exchange & price movement:**
- 🟠⚫️ - exchange icons (Bybit in this case). Each exchange has its own set of colored circles for quick visual identification.
- [Bybit](link) - clickable link directly to the **trading page** for this contract on the exchange.
- 10.86% (0.13374 - 0.14826) - price change over the period (%), start and end prices.
- 🔼 OI: 9.77% (1.64M - 1.80M) - open interest change over the same period, absolute values in USDT.
- 🛢 Volume: 3.37% (12.36M - 12.77M) - trading volume change over the period, absolute values.

**Technical indicators:**
- 🔄 RSI: 76.04% / 71.11% / 64.97% - RSI on timeframes **15m / 1h / 1d**. All three values are elevated here - the coin is overbought across all horizons.
- 📶 Funding: 0.005% - current funding rate. Positive = longs pay shorts. Near zero = neutral.
- 🔋 Rank: #1046 - coin's position in the global market cap ranking.
- 🔊 Signal/24H: 3 - how many times this screener has already fired for this coin today. Helps gauge how "fresh" the signal is.
- 📈 Change 1h/24h: 11.55% / 14.53% - price change over the last hour and last 24 hours.
- 🌍 Global Vol 24h: $36.7M (V/MC: 310.8%) - total trading volume for this coin across all exchanges over 24h. V/MC is the volume-to-market-cap ratio; 310% means that in one day, the equivalent of 3x the coin's entire market cap passed through the market - a sign of very high activity.
- 🪙 Circulation: 97.76% - percentage of coins in circulation vs maximum possible supply. The higher it is, the more coins are distributed among holders, which means a lower risk of various price manipulations by the project team.
- 🧪 Innovation Zone - a special exchange zone for new or experimental projects. These coins are usually exposed to very high volatility.

**Fundamentals block** (only in the Ticker card, not in the "All Exchanges" view and not in screener signals):

```
📊 Fundamentals:
💰 MCap/FDV: $17.0M / $17.4M
⚖️ Inflation Gap: +2.29% | 🟢 Safe
🌍 Global Vol: $69.3M (V/MC: 406.35%)
🪙 Circulation: 97.76%
📉 From ATH: -86.3%
📈 From ATL: +260.3%
```

- 💰 MCap/FDV: $17.0M / $17.4M - market cap (only circulating coins) / fully diluted valuation (all coins including unreleased). The closer MCap is to FDV - the better.
- ⚖️ Inflation Gap: +2.29% | 🟢 Safe - the gap between MCap and FDV as a percentage. Shows how many "hidden" tokens haven't hit the market yet. Tiers: 🟢 Safe (< 15%), 🟡 Mid Risk (< 50%), 🔴 High Risk (≥ 50%).
- 🌍 Global Vol: $69.3M (V/MC: 406.35%) - described above.
- 🪙 Circulation: 97.76% - described above.
- 📉 From ATH: -86.3% - drop from all-time high.
- 📈 From ATL: +260.3% - rise from all-time low.

---

### Buttons under a signal

Each screener signal comes with quick-action buttons:

| 📉 Short | Blacklist | 📈 Long |
|---|---|---|
| 📊 Chart | ℹ️ Ticker |  |

- **📉 Short** - open a short position on this coin on the exchange that sent the signal (uses settings from Trade Settings).
- **Blacklist** - add the coin to the blacklist for this exchange. It will stop generating signals.
- **📈 Long** - open a long position on this coin.
- **📊 Chart** - get a candlestick chart directly in the chat (15m by default, switchable).
- **ℹ️ Ticker** - get an up-to-date card for the coin with current market data: price, RSI, funding, volume, Fundamentals. Useful when you need to quickly refresh data before making a decision - especially if the signal arrived a few minutes ago.

---

<a id="6-screeners-section"></a>
## 6. Screeners Section

Press **🖥 Screeners** and choose an exchange (Bybit, Binance, OKX, Bitget). Each exchange has an on/off toggle - it controls whether signals from that exchange will be delivered. There is also a **🌐 InterExchange Screeners** button for access to cross-exchange screeners.

After selecting an exchange, the **Exchange Main Menu** opens with five sections:

| Button | Purpose |
|---|---|
| 🖥 Screeners Settings | List and settings of all screeners, including filters |
| 🧮 Signals Count | Number of signals per screener for today |
| 🧾 Signals Log | Export all signals for 1/3/7 days as `.csv` |
| ⚙️ Tickers | Whitelist/blacklist, new coin filtering, innovations |
| 🔍 One-time Request | One-time screener for the current exchange without saving settings |

<a id="61-screener-settings"></a>
### 6.1 Screener Settings

The Screener Settings section shows all available screeners for the selected exchange:

- **Bybit, Binance:** Screeners 1–9 (all types)
- **OKX:** Screeners 1–6 (pump/dump + hour + multi)
- **Bitget:** Screeners 3–6 (hour and multi only)

Each screener shows its main parameters on the left and a **Filters** button on the right. Tapping a screener opens its submenu with buttons: **🖊 New Values**, **Filters**, **⚙️ Tickers Selection: Turn On/Turn Off**.

Screener list example:

| Screener | Settings |
|---|---|
| 🔹 Price Pump | Filters |
| 🔻 Price Dump | Filters |
| ✂️ Liquidations | Filters |

<a id="611-screeners-1-2-pump-dump"></a>
#### 6.1.1 Screeners 1, 2: Pump & Dump

Minute-level screeners for scalping. Search for price pumps and dumps over periods from 1 to 30 minutes, data updates every 3 seconds.

**Setup format:** `lower-upper period`

For example, `1-3 5` - send a signal if the price rose between 1% and 3% in 5 minutes.

For dumps, the setup is the same - the bot searches for drops automatically, no negative values needed.

**Markers:** 🔹 - pump, 🔻 - dump.

Settings screen example:

```
Exchange: 🟠 Bybit
Screener: 🔹 Price Pump

Allowed range:
Min: 1.5%
Max: 6%
Period: 5 min

Current screener filters:
      🔺 Vol Change: 20 400
      🔄 RSI/15m: 45 78
      🔄 RSI/1h: 📵 Disabled
      📶 Funding: -0.2 0.2
      🔋 Cap: <500
      🪙 Circulation: >55
      🛢 Daily Vol: >25
      🔊 Signals / 24h: <4

⚙️ Ticker Selection: Enabled
```

For dumps, the screen is the same, but with `🔻 Price Dump` and its own values, for example `2-8 3`.

<a id="612-screeners-3-4-hourscreeners"></a>
#### 6.1.2 Screeners 3, 4: HourScreeners

Hourly screeners. Monitor price changes over periods from 1 to 24 hours, updated every minute.

**Setup format:** `lower upper period`

Values include sign - you define the direction yourself. For example, `-10 -3 3` - dump of 3% to 10% over 3 hours. `3 10 6` - pump of 3% to 10% over 6 hours.

**Markers:** 🔶 - HourScreener 1, 🔸 - HourScreener 2.

Settings screen example:

```
Exchange: 🟠 Bybit
Screener: 🔶 HourScreener/1st

Allowed range:
Min: -12%
Max: -4%
Period: 3 hour

Current screener filters:
      🔄 RSI/15m: 20 55
      🔄 RSI/1h: 25 60
      🔄 RSI/1d: 📵 Disabled
      📶 Funding: -1 1
      🔋 Cap: <800
      🛢 Daily Vol: >15
      🔊 Signals / 24h: <3

⚙️ Ticker Selection: Enabled
```

The second HourScreener can keep a separate scenario, for example `4 11 6` for a medium-term pump over 6 hours.

<a id="613-screener-5-liquidations"></a>
#### 6.1.3 Screener 5: Liquidations

Monitors forced liquidations of other traders' positions. Configurable options:
- **Amount threshold** - minimum liquidation size in USDT to notify
- **Direction** - long liquidations only, short only, or both
- **Separate thresholds** for each direction

It's practical to set higher thresholds for Binance (far more liquidations) and lower for Bybit.

For Binance, the screener uses the futures market liquidation stream and only counts USDⓈ-M events.
Binance signals are sent only when the current funding rate is available, because the funding rate is shown in the liquidation text.

**Markers:** 🔴 - long liquidation, 🟢 - short liquidation.

Settings screen example:

```
Exchange: 🟠 Bybit
Screener: ✂️ Liquidations

Current liquidation thresholds:
🟢 Long: $120k
🔴 Short: $90k

Current screener filters:
      ↔️ Side: 🔴🟢 All
      🔋 Cap: <700
      🛢 Daily Vol: >40
      🔊 Signals / 24h: <5

⚙️ Ticker Selection: Disabled
```

<a id="614-screeners-6-7-multiscreeners"></a>
#### 6.1.4 Screeners 6, 7: MultiScreeners

Monitor three indicators simultaneously: price change, OI change and volume change. Configured using threshold values with comparison signs.

**Setup format:** `>price >oi >volume period`

For example, `>5 >5 >10 10` - send a signal if over 10 minutes: price rose >5%, OI rose >5%, volume rose >10%. Use `<` to search for decreases.

**Markers:** 🎛 - MultiScreener 1, 🎚 - MultiScreener 2.

Settings screen example:

```
Exchange: 🟠 Bybit
Screener: 🎛 MultiScreener/1st

Current enabled settings:
💰 Price > than 4%
🔼 OI > than 6%
🛢 Volume > than 12%
Period: 10 min

Current screener filters:
      🔄 RSI/15m: 45 82
      🔄 RSI/1h: 35 75
      📶 Funding: -0.3 0.3
      🔋 Cap: <600
      🛢 Daily Vol: >30
      🔊 Signals / 24h: <4

⚙️ Ticker Selection: Enabled
```

The second MultiScreener is useful for the opposite scenario, for example `<3 <5 <10 15`.

<a id="615-screeners-8-9-funding"></a>
#### 6.1.5 Screeners 8, 9: Funding

Monitor the funding rate before its settlement. Allow you to receive a signal in advance - for example, 10–15 minutes before settlement - and open a position in anticipation of the payout.

**Setup format:** `funding_min funding_max / time_min time_max`

Both funding values must have the same sign. For example, `-1 -0.5 / 10 15` - send a signal if funding is between -1% and -0.5%, within 10–15 minutes before settlement. At such moments it can be worth opening a long: negative funding is paid to longs, and shorts often close before settlement, pushing the price up.

**Markers:** 📶 - Funding Screener 1, 🛜 - Funding Screener 2.

Settings screen example:

```
Exchange: 🟠 Bybit
Screener: 📶 Funding/1st

Allowed range:
Min: -1.2%
Max: -0.4%
Send within: 8-18min

Current screener filters:
      🔄 RSI/15m: 25 70
      🔄 RSI/1h: 30 75
      🔋 Cap: <900
      🛢 Daily Vol: >20
      🔊 Signals / 24h: <3

⚙️ Ticker Selection: Enabled
```

<a id="616-listings-and-delistings"></a>
#### 6.1.6 Listings and Delistings

The bot also sends informational signals about new listings and delistings. Functionally, this is a separate screener without configurable price, OI or RSI thresholds: it reports an exchange event rather than a market move.

Listing signal example:

```
📌 KLACUSDT New Listing!
🟠⚫️ Bybit price: $253.01
```

The ticker in the signal opens Coinglass, and the exchange name opens the contract trading page. New listings are often highly volatile, so in **⚙️ Tickers** you can enable auto-blacklist for new tickers with **Auto / On** and set the filtering period with **⏲️ Timer**. Delisting signals should be treated as risk signals: liquidity and price behavior can deteriorate sharply before a contract is removed.

<a id="617-screener-filters"></a>
#### 6.1.7 Screener Filters

Filters are the main competitive advantage of these screeners. They allow pre-filtering signals by additional market parameters before the notification is sent.

Available filters (set depends on screener):

| Filter | Description | Format |
|---|---|---|
| RSI 15m / 1h / 1d | Exclude overbought or oversold coins | `40 70` (range) |
| Volume Change | Filter by volume change over the period (Screeners 1, 2 only) | `20 100` |
| Market Cap | By ranking position in the top (market cap rank) | `>10`, `<200`, `10 100` |
| Circulation | By % of coins in circulation vs max supply (Screeners 1, 2 only) | `>60`, `50 100` |
| Funding | Funding rate range within which the signal passes | `-0.1 0.1` |
| Daily Volume | Minimum daily trading volume (millions USDT) | `>50`, `20 500` |
| Day Limit | Max number of signals per ticker in this screener per day | `<5`, `2 5` |

The **Circulation filter** is especially useful: coins with a low circulation percentage (below 30–40%) carry elevated risk from two directions. First, the project team can dump reserved tokens on the market at any time and crash the price. Second, and this is important to understand: low circulation means a small free float - market makers need relatively little capital to pump such a coin dozens of times upward, lure in retail buyers, and then dump sharply. In other words, the fewer coins in free circulation, the easier it is to manipulate the price in both directions. Setting `>50` or `>70` ensures you only trade coins with a sufficiently "unlocked" supply.

The **Day Limit filter** is useful in two scenarios. Let's use a pump screener as an example. The first scenario is filtering out extra signal spam for a coin: if you trade longs and already entered near the start of the move on the first signal, you can limit signal delivery with `<2` so you do not keep receiving more signals for the same coin. The second scenario is the opposite - start receiving signals only after a predefined threshold, for example `>5`. This is useful for shorts: instead of entering on the first impulses from the lows, you wait until the move becomes more extended.

Input format examples: `<3` - the 1st and 2nd signals per ticker per day will be delivered, `>5` - signals starting from the 6th will be delivered, `2 5` - signals from the 2nd through the 5th will be delivered.

<a id="618-setting-parameters"></a>
#### 6.1.8 Setting Parameters

When entering parameters, three buttons appear below the message:

| Button | Purpose |
|---|---|
| 📵 Disable Screener | Clear current screener parameters |
| ⚙️ Tickers Selection | Enable/disable filtering by ticker lists |
| ❌ Cancel input | Close input without changes |

- **📵 Disable Screener** - clear settings, no more signals from this screener
- **⚙️ Tickers Selection: Turn On/Turn Off** - enable/disable the whitelist/blacklist for this specific screener (useful when you want one screener to see all market coins while others filter by your list)
- **❌ Cancel input** - close the dialog without changes

<a id="619-screener-configurations"></a>
#### 6.1.9 Screener Configurations

The bot allows you to save current screener and filter settings as named configurations - up to 3 per exchange. Useful for working with multiple strategies: morning volatility, flat market, trending conditions. Accessible via the **💾 Configs** button in the exchange screener menu. Name: up to 10 Latin characters or digits.

<a id="62-signal-counter"></a>
### 6.2 Signal Counter

Displays the number of signals per screener for the current day. Switch between screeners using buttons and see which coins triggered each one and how many times. Useful for assessing current market volatility through the lens of your settings: if a screener is silent all day - either the parameters are too tight or the market is flat. Resets at 7:00 UTC daily or manually.

Example:

```text
Bybit / Signals Count
🔹 Pump: 14
🔻 Dump: 9
✂️ Liquidations: 23
```

<a id="63-signal-log"></a>
### 6.3 Signal Log

Export all signals for the selected exchange for **1, 3 or 7 days** as a `.csv` file. The file contains the time, ticker, screener and key metrics at the moment of the signal. Useful for strategy analysis: check what time of day signals are most frequent, which coins trigger most often, and adjust settings accordingly.

Period buttons:

| 1 day | 3 days | 7 days |
|---|---|---|
| 1-day CSV | 3-day CSV | 7-day CSV |

CSV row example:

```text
created_at,exchange,screener,ticker,price,payload
2026-07-01 12:10:35,bybit,1,BTCUSDT,64250.5,{...}
```

A 30-second cooldown applies between exports.

<a id="64-tickers"></a>
### 6.4 Tickers

A filtering mechanism that applies to **all screeners** on the selected exchange.

**Whitelist** - coins that are allowed to generate signals. If the list is not empty, the bot will only pass through signals **for these coins and nothing else**. Manage via **Whitelist +** and **Whitelist –**. Both `BTCUSDT` and `BTC` formats are accepted.

**Blacklist** - coins excluded from signals. Only applies when the whitelist is empty: if the whitelist is populated, the blacklist is ignored. Manage via **Blacklist +** and **Blacklist –**.

**Auto-blacklist for new tickers** - when enabled (the **Auto / On** button), the bot automatically adds newly listed coins to a separate blacklist immediately after an announcement. New coins often behave unpredictably - this feature protects against accidental entries. The **⏲️ Timer** button sets how many days before a coin is automatically removed from this list.

**Innovations** (**Innovation / On** and **Innovation / Off** buttons) - when enabled, signals include a ✨ suffix if the coin has entered this screener's range for the first time in the current monitoring period. Helps distinguish fresh moves from repeated triggers on "stuck" coins.

**Signal Limit** - maximum number of signals per ticker per screener per day. As of the current version, this parameter has been moved to the filters of each individual screener (the **🔊 Signals/24h** button).

Ticker menu example:

| Button | Purpose |
|---|---|
| Whitelist + / Whitelist – | Add or remove allowed tickers |
| Blacklist + / Blacklist – | Add or remove blocked tickers |
| Auto / On | Automatically hide new listings |
| Innovation / On | Mark fresh moves in signals |

Ticker input example:

```text
BTC ETH SOL
BTCUSDT,ETHUSDT,SOLUSDT
```

<a id="65-one-time-request"></a>
### 6.5 One-time Request

The **🔍 One-time Request** button runs a one-time screener for the current exchange. It does not change regular screener settings and does not save a configuration: you enter conditions, the bot checks live data for the selected exchange and sends back the matching coins.

Input format: conditions separated by `;`. All conditions work as AND, so a coin must pass every condition you specify.

Available parameters:

- `circulation <15` - circulating supply is below 15% of max/total supply.
- `volume >3` - exchange 24h volume is above 3M USDT.
- `funding -0.5 0.5` - funding is between -0.5% and 0.5%.
- `rsi_15m 30-70` - 15m RSI range.
- `rsi_1h 30-70` - 1h RSI range.
- `rsi_1d 30-70` - 1d RSI range.
- `cap <800` - CoinGecko market cap rank is below 800.
- `limit 20` - return up to 20 coins.
- `sort circulation asc` - sort by circulation ascending.
- `sort volume desc` - sort by volume descending.

Examples:

```text
circulation <15; limit 20
circulation <15; volume >3; cap <800; limit 20
circulation <10; funding -0.5 0.5; rsi_1h 30-70; sort circulation asc
```

After receiving the result, it can be removed with the **❌ Hide window** button. One-time requests are limited to one successful request every 30 seconds per user.

---

<a id="7-cross-exchange-screeners"></a>
## 7. Cross-Exchange Screeners

Accessible via the **🌐 InterExchange Screeners** button in the exchange selection menu.

InterExchange overview example:

```
🌐 Inter-Exchange Screeners:

🌐 Active Exchanges:
    Bybit | Binance | OKX | Bitget

Long filters:
    🔄 RSI/15m: 25 70 | 🔄 RSI/1h: 30 75 | 🛢 Daily Vol: >20

Short filters:
    🔄 RSI/15m: 55 90 | 🔄 RSI/1h: 60 95 | 🛢 Daily Vol: >20

📶 Funding:
    Spread: 0.7%

🔹 Price:
    Spread: 2.4%
```

<a id="71-interfunding"></a>
### 7.1 InterFunding

Compares funding rates for the same coin across multiple exchanges simultaneously. The goal is to find situations where one exchange has a positive funding rate (longs pay shorts) and another has a negative rate (shorts pay longs). By opening a long on the negative-funding exchange and a short on the positive-funding exchange, you receive payouts from both sides while neutralizing price risk.

**Setup:** a single threshold value for the funding rate difference (e.g. `0.5` - only trigger when the difference is ≥ 0.5%). The signal will specify the exact exchanges and recommended directions.

Signal example:

```text
📶 InterFunding / BTCUSDT
🟢 Long: Binance / Funding: -0.42%
🔴 Short: Bybit / Funding: +0.31%
Spread: 0.73%
```

Additional profit is possible if the price on the long exchange is lower than on the short exchange - convergence creates another profit source.

<a id="72-interprice"></a>
### 7.2 InterPrice

Monitors price differences for identical contracts across exchanges. Every minute, the bot compares prices for coins present on at least 2 exchanges and sends a signal when the spread exceeds your threshold.

**Setup:** threshold percentage (minimum 2%; e.g. `0.3` - trigger when spread ≥ 0.3%).

Signal example:

```text
🔹 InterPrice / SOLUSDT
🟢 Long: OKX / Price: 185.20
🔴 Short: Binance / Price: 189.40
Spread: 2.27%
```

The signal includes a **💵 Open Deal** button - it instantly opens two positions (long and short) on the right exchanges in the correct directions, provided you have API keys connected for both.

Buttons below an inter-exchange signal:

| 🚫 Exclude | 🔄 Refresh |
|---|---|
| 💵 Open Deal | |

- **💵 Open Deal** - open paired positions.
- **🚫 Exclude** - mute the pair.
- **🔄 Refresh** - refresh pair data.

A **Counter** is also available for viewing InterFunding and InterPrice signals for the day.

<a id="73-filters-pair-exclusion"></a>
### 7.3 Filters & Pair Exclusion

For each cross-exchange screener, RSI filters can be configured **separately for each leg** - for the exchange with the long (long leg) and the exchange with the short (short leg). For example, you can block a signal if the long-side exchange is overbought on the 1d RSI.

Filters are accessible via the **🟢 Long Filters** and **🔴 Short Filters** buttons in the InterFunding or InterPrice menu.

**Pair exclusion:** directly from a signal, you can mute a specific pair - for 1 day, 1 week, or 1 month. Press **🚫 Exclude** → select period. Useful when a pair keeps triggering but you don't plan to trade it.

Exclusion period buttons:

| 1 day | 1 week | 1 month |
|---|---|---|
| Back | | |

---

<a id="8-trading-section"></a>
## 8. API Section

Press **📡 API** from the main menu. Everything related to live trading is here.

**API main menu:**

| Button | Purpose |
|---|---|
| 🛠 Trade Settings | Entry parameters, TP, SL, averaging for each exchange |
| 🏧 Autotrading | Link screener markers to automatic position opening |
| 📂 Positions - Info | Compact list of all open positions in one message |
| 📂 Positions - Mng. | Open position cards with management buttons |
| 💵 Balance | Free and locked balance across all exchanges |
| 📋 PNL / Log | 30-day PNL, trade history, chart |
| 📦 Markets Menu | Exchange connections, API key management |
| Exchange Events | Toggle notification mode (all events / important only) |

<a id="81-markets-menu-exchange-connections-api-keys"></a>
### 8.1 Markets Menu - Exchange Connections & API Keys

#### Generating Keys

In **📦 Markets Menu**, select **🔑 Manage API keys** → the exchange → **🔑 Set keys**. The bot will ask for:
- **API Key** - public key
- **API Secret** - secret key
- **Password** - additional passphrase (OKX, Bitget, KuCoin only)
- **UID** - identifier (Gate only)

Markets menu keyboard:

| Button | Purpose |
|---|---|
| 🔌 Manage markets | Create or disconnect an exchange instance |
| 🔑 Manage API keys | Set or remove API keys |
| ◀️ Back | Return to the API main menu |

When generating keys on the exchange, **make sure no checkboxes are selected** in the "Assets" / "Withdrawals" section - keys must not have withdrawal permissions. Only select permissions related to trading.

For Bybit, it's recommended to create a sub-account, deposit a minimal amount, and generate keys in the API Management section on the exchange website.

#### Connecting an Exchange (Creating an Instance)

After entering keys, go to **🔌 Manage markets** and tap the target exchange. The bot creates an instance (WebSocket connection) and a ✅ will appear next to the exchange. Tapping again disconnects the exchange and closes all streams.

Exchange status example:

```text
✅ Bybit
✅ Binance
OKX
Bitget
```

**Testnet:** when creating an instance in **🔌 Manage markets**, there is a **☑️ Test-net mode** / **✅ Main-net mode** button - switches demo/main mode for all exchanges. The key entry process is the same, but testnet keys must be generated in the exchange's Testnet section.

#### Important Warning

By connecting keys, you are giving the bot the ability to trade with your funds. You control the key permissions and bear full responsibility for the safety of your funds. Start with a minimal deposit.

<a id="82-trade-configs-trading-settings"></a>
### 8.2 Trade Settings

The main trading configuration menu. This is where the bot's behavior is defined when opening and managing positions. Settings are fully separate for **📈 Long** and **📉 Short** - you can configure different logic for each direction. The currently selected direction is shown after the action label.

Settings menu buttons:

| Button | Purpose |
|---|---|
| 💵 Size | Position size |
| 📤 Order | Market/Limit and limit parameters |
| 🎚 Price Delta | Price offset for a limit order |
| ⏲️ Limit Lifetime | Limit order lifetime |
| 💰 TP | Take-profit and auto-refill |
| 🚫 SL | Stop-loss and SL movement |
| 🔁 Averaging | Step or grid averaging |
| ↔️ Mode | Hedge / One-way |
| ⏏️ Leverage | Minimum and desired leverage |
| 🔗 Position Limit | Maximum open positions |
| 📈 Long / 📉 Short | Switch settings direction |
| 💾 Configs | Save, load or delete a config |
| ◀️ Back | Go back |

Example of current trading settings:

```
Current trading settings:
Exchange: 🟠 Bybit | Action: 📈 Long

💵 Size: 6.0% of Deposit
📤 Order Type: Limit | Delta: 0% | Lifetime: 2 min
💰 TP: 100.0% / 4 / Limit
🚫 SL: Disabled
⏫ Refill After TP: Enabled
🔁 Averaging: Disabled
↔️ Mode: Hedge
⏏️ Leverage: 3x / 3x
🔗 Position Limit: 2
```

<a id="821-position-size"></a>
#### 8.2.1 Position Size

Entry size: as a percentage of total balance (free + in positions) or a fixed USDT amount. Units (percentage / USDT) are toggled with a button after entering the value.

Recommendation: start with a small fixed size (5–20 USDT) until you understand how the bot behaves. Percentage mode is convenient as the deposit grows - position sizes scale automatically.

<a id="822-order-type"></a>
#### 8.2.2 Order Type

- **Market** - instant execution, but with taker fee and possible slippage.
- **Limit** - saves on maker fee, no slippage, but no guarantee of execution. From experience, 70–80% of limit orders fill.

When choosing limit orders, two additional settings appear:

- **Price Delta** - offset the order from the current price as a percentage. Positive value shifts the order higher (increases fill probability at a slightly worse entry). Negative - lower (if you expect continued favorable movement before a reversal).
- **Limit Lifetime** - limit order lifetime in minutes. After this time expires, the bot deletes only limit orders placed by the bot itself. **Important:** with a short screener period (1–2 min) and a long limit lifetime, the bot may queue multiple orders that all fill later, bloating the position. Set the lifetime shorter than the minimum screener period.

<a id="823-tp-take-profit"></a>
#### 8.2.3 TP - Take-Profit

Configured with 1–3 parameters: `level [count] [slippage]`

- **Level** - percentage from entry price where the order is placed. Example: `2` - take-profit at +2% from entry.
- **Count** (1–5, default 1) - if > 1, the position is split into equal parts and TPs are spaced evenly. Example: `2 3` - three take-profits at 2%, 4% and 6% from entry.
- **Slippage** (0 = limit TP; > 0 = trigger order with callback from best price).

When a grid TP fires, the bot automatically recalculates averaging orders (reduced position size) and the stop-loss.

Example: `2 3` creates three take-profits at 2%, 4% and 6% from entry.

**Auto-Refill** - enabled in TP settings. After a grid TP fires, a limit refill order for the same size is placed. Placement price: entry − offset (long), entry + offset (short). When the next TP fires, the previous refill is cancelled and replaced with one accounting for accumulated volume. If the order fills - entry price improves, the averaging grid is recalculated. Auto-refill doesn't increase risk because it only triggers after profit-taking.

<a id="824-sl-stop-loss"></a>
#### 8.2.4 SL - Stop-Loss

A single value - the stop-loss level as a percentage from entry. Example: `3` - SL triggers at a 3% drop from entry. Implemented as a triggered market order (previously limit - changed to prevent non-execution on fast moves).

Example: if entry is `100`, SL `3` triggers near `97` for a long and near `103` for a short.

**Move SL** - when enabled, a new SL position is automatically set each time a grid TP fires. Examples: `0` - SL moves to breakeven (entry price); `1` - SL moves to 1% above entry, locking in a minimum profit.

<a id="825-averaging"></a>
#### 8.2.5 Averaging

Working with averaging is extremely dangerous and requires understanding - poor averaging can lead to liquidation of the position or the entire deposit. Read carefully!

**Input format:** `offset% size% count`, e.g. `10 100 4` - 4 averaging steps, each 10% apart from the previous, sized at 100% of the current position.

Two modes:

**Step Averaging** - orders placed one at a time. After the first fills, the bot cancels all stop orders, updates the entry price and size, places a new SL, and queues the next step from the grid. Doesn't lock all capital at once - convenient with a limited deposit, but may miss fast moves.

**Batch Grid** - all averaging orders placed immediately. With settings `10 100 4` and a starting position of 10 coins, the bot places four orders: 10, 20, 40 and 80 coins (each successive order accounts for accumulated volume). The SL doesn't move with the entry price - only its volume changes. Locks capital, but no sharp move will be missed.

Averaging grid example `10 100 4`:

| Step | Offset from entry | Size |
|---|---|---|
| 1 | 10% | 100% of current position |
| 2 | 20% | 100% of accumulated size |
| 3 | 30% | 100% of accumulated size |
| 4 | 40% | 100% of accumulated size |

Manual averaging (from the bot or exchange) automatically recalculates all orders.

<a id="826-position-mode"></a>
#### 8.2.6 Position Mode

- **Hedge** - allows holding both long and short for the same coin simultaneously. Used for cross-exchange arbitrage and hedging losing positions.
- **One-way** - opening a short while a long is open will reduce the long rather than creating a separate position.

<a id="827-leverage"></a>
#### 8.2.7 Leverage

From 1 to 100. Enter one or two values separated by space: minimum and wanted leverage. If one value is entered, it is used as both minimum and wanted leverage. First, the bot compares the minimum leverage with the coin maximum leverage when the exchange provides that value: if the minimum is higher than the maximum - the position is not opened and the bot shows an error. If the minimum is allowed, the bot applies the lower value between the coin maximum leverage and the user wanted leverage; if the exchange does not provide a maximum, the bot applies the wanted leverage. Why is this needed? The coin maximum leverage is also a kind of coin characteristic provided by the exchange, and it can be used as an extra reference point. Weak and "unreliable" coins often have maximum leverage no higher than 5. The minimum leverage parameter helps filter out exactly those coins.

Examples:

- `10 20`, coin maximum `5x` - error.
- `10 20`, coin maximum `15x` - the bot sets `15x`.
- `10 20`, coin maximum `25x` - the bot sets `20x`.

Note that high leverage significantly lowers the liquidation price. Starting value recommended: 5–10×.

Example bot error:

```
🟠⚫️ Bybit / BTCUSDT / ❗️ long position opening error

`Minimum leverage 10x is higher than max allowed 5x for BTC/USDT:USDT`
```

<a id="828-position-limits"></a>
#### 8.2.8 Position Limits

Maximum number of simultaneously open positions per direction. When reached, autotrading won't open new positions - even if a signal arrives. A very useful protection in volatile markets. Starting value recommended: 1–2.

<a id="829-trading-configurations"></a>
#### 8.2.9 Trading Configurations

Same as screener configs - save up to 3 trading configs per exchange and switch between them quickly. For example: one config for aggressive trading with high leverage and grids, another for conservative trading with small size and no averaging.

### 8.3 Autotrading - Automatic Position Opening

The tool for linking screener markers to automatic position opening.

Go to **🏧 Autotrading → 💶 Set Markers**, choose an exchange. For each exchange, two sets of markers are configured: for longs and for shorts.

**Full marker list:**

| Marker | Screener |
|---|---|
| 🔹 | Price Pump (Screener 1) |
| 🔻 | Price Dump (Screener 2) |
| 🔶 | HourScreener 1 (Screener 3) |
| 🔸 | HourScreener 2 (Screener 4) |
| 🔴 | Long Liquidation (Screener 5) |
| 🟢 | Short Liquidation (Screener 5) |
| 🎛 | MultiScreener 1 (Screener 6) |
| 🎚 | MultiScreener 2 (Screener 7) |
| 📶 | Funding Screener 1 (Screener 8) |
| 🛜 | Funding Screener 2 (Screener 9) |

Example: to open longs on dumps and short liquidations - add 🔻 and 🟢 to Long Markers.

Markers screen example:

```
Set autotrading markers:
Market: 🟠 Bybit / Action: 📈 Long

For long positions: 🔻 🟢 📶

For short positions: 🔹 🔴 🎛
```

**Autotrading on/off per exchange** - the Autotrading menu has an individual toggle per exchange and also for cross-exchange autotrading (Inter).

Autotrading keyboard example:

| Button |
|---|
| 🔴 Bybit |
| 🟢 Binance |
| 🔴 Okx |
| 🟢 Bitget |
| 🔴 InterExchange |
| 💶 Set Markers |
| ◀️ Back |

**Alerts mode** - in the API main menu there is an **Exchange Events** toggle: "Important events only" (order fills) or "All events" (all bot actions).

<a id="84-positions-info-management"></a>
### 8.4 Positions - Info & Management

Press **📂 Positions - Info** to get one compact text block with all open positions. Positions are grouped by exchange: exchange link first, then position lines with clickable tickers and PNL, then total PNL for that exchange. Each position uses two lines: the first line shows ticker, side, current coin price and position cost, the second line shows Change, total PNL and unrealized/realized PNL in brackets. PNL below zero is marked 🔴, zero and profit are marked 🟢. The **❌ Hide** button deletes the list message, **🔄 Refresh** updates the data in the same message.

Example:

```
Bybit
BTCUSDT / L / 64247.50 / $628.80
+1.98% / 🟢 PNL: +12.45 (+10.35 / +2.10)

ETHUSDT / S / 3425.16 / $418.90
-0.74% / 🔴 PNL: -3.10 (-3.10 / +0.00)

PNL: +9.35
```

Press **📂 Positions - Mng.** to see open position cards across all exchanges.

**Short position card:**

```
⏺️ Bybit / SOLUSDT / 🟢 Long
Entry: 185.40 | Size: $92.70
Price: 189.20 | Liq.: 160.50
Strategy: ⏺️ Bybit
PNL: $1.84 (1.98%)
```

Buttons on the short card:
- **ℹ️ Ticker** - open full market data for the coin
- **More** (green/red depending on PNL) - expand detailed position view

**Detailed position view** adds:
- **Close** - partially (25%, 50%) or fully (100%)
- **Average** - add to position at 100, 200, 400 or 500% of current size
- **Hedge** - open an opposite position of the same size
- **Grid** - view and edit the averaging grid manually (comma-separated price levels) or delete it
- **Orders** - list of all active orders for the position (TP, SL, averages, auto-refills) with delete or edit capability per order (price or size)
- **📊 Chart** - candlestick chart with orders marked and current PNL displayed. Available timeframes: 15m, 1h, 1d

When editing an order, the bot deletes the old one and creates a new one with the updated parameters (most exchanges don't support direct order modification via API).

<a id="85-balance"></a>
### 8.5 Balance

Displays available balance per connected exchange:

```
Bybit / USDT Balance:
💵 Free: $210.50
📈 In Positions: $92.70
💰 Total: $303.20
```

<a id="86-pnl-trade-history-statistics"></a>
### 8.6 PNL - Trade History & Statistics

Statistics section for closed trades executed by the bot via API.

Pressing **📋 PNL / Log** shows a summary:
```
PNL for last 30 days (closed trades): +$42.15
Trades: 38
```

Available actions:
- **Trade History** - `.csv` export for 1 day, 7 days or 1 month. Contains all closed trades with timestamp, ticker, direction and PNL.
- **Chart** - visual bar chart of daily PNL for 30 days with total summary. Shows at a glance which days were profitable and which were losses. A cooldown applies between chart requests.

Section buttons:

| Trade History | Chart |
|---|---|

Trade history period buttons:

| 1 day | 7 days | 1 month |
|---|---|---|
| ◀️ Back | | |

This section helps evaluate strategy effectiveness over time and decide whether to adjust settings.

<a id="87-exchange-events"></a>
### 8.7 Exchange Events

The **Exchange Events** button is in the API main menu next to **📦 Markets Menu**. It switches notification mode:

- **Important events only** - the bot sends notifications about filled orders.
- **All events** - the bot sends all trading events and position actions.

---

<a id="9-account-subscription"></a>
## 9. Account & Subscription

Accessible via the `/profile` command. The account keyboard is used inside this section.

Profile screen example:

```text
User ID: 123456789
Invited by: Admin
First name: Alex
Access till: 2026-08-01
Current plan: Pro
Available balance: 15 USDT
```

Account buttons:

| Button | Purpose |
|---|---|
| 👨🏻‍💻 Account | Profile and subscription |
| 💵 Balance / Plan | Top up and plans |
| 👨‍👦‍👦 Referrals | Referral program |
| 🗿 Language | Switch language |

- **👨🏻‍💻 Account** - shows name, ID, current plan, subscription expiry date and balance
- **💵 Balance / Plan** - top up balance and choose a subscription tier
- **👨‍👦‍👦 Referrals** - referral program: your code and list of invited users
- **🗿 Language** - switch interface language (RU / EN)

**Payment** is made in cryptocurrency (USDT TRC-20, USDT TON, TON) to the provided address. After transferring, press the "I Paid" button - an admin will verify and credit the funds.

**Plans** differ in available features (number of exchanges, autotrading, cross-exchange screeners) and duration.

New users start with Bybit enabled by default. The starter preset adjusts Bybit screener_1, screener_3, and screener_1 filters to reduce noisy signals.
