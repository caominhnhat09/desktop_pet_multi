<div align="center">

# 🐾 Desktop Pet

**A living AI companion that lives on your Windows desktop.**  
Learns who you are. Reacts to your work. Keeps you from skipping your breaks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![GitHub Stars](https://img.shields.io/github/stars/chron303/desktop-pet?style=social)](https://github.com/chron303/desktop-pet)

[**Build the .exe**](#option-1--build-the-exe) • [Report Bug](https://github.com/chron303/desktop-pet/issues) • [Request Feature](https://github.com/chron303/desktop-pet/issues)

</div>

---

## What is Desktop Pet?

Desktop Pet is a pixel-art companion that lives in the corner of your screen. It's not a screensaver or a widget — it's something closer to a real pet. It notices what apps you're using, reacts to your music, remembers facts you tell it, gets hungry, levels up, and develops a personality over time. It also acts as a focus coach: it runs Pomodoro sessions and refuses to let you skip your breaks.

It runs locally. Your data stays on your machine. No accounts, no cloud, no subscriptions.
(The one network exception is speech-to-text: voice commands use Google Web Speech by default and fall back to offline recognition when you are offline.)

---

## Features

### 🐶 🐉 🐱 Three Pets, 24-30 Animations Each
Switch between a Dog (30 animations), Dragon (24) or Cat (30) at any time. Each has its own animations, personality system, wake words, and fallback responses. The dragon is proud and majestic. The cat is delightfully aloof. The dog just wants to play.

### 🧠 Local AI Brain
Powered by [Ollama](https://ollama.ai) running locally on your PC. No API keys needed for the AI. Uses `gemma2:2b` by default — fast enough for an i3 processor. The pet responds to voice commands and typed messages in character, with personality-appropriate replies. Without Ollama it falls back to built-in personality-matched lines.

### 💭 Continuous Emotion Engine
The pet's mood isn't a string that gets set and forgotten. It's a live 2D state (valence + arousal) that drifts continuously based on hunger, time of day, music, app context, and how long since you last interacted. Feed it and watch the mood spike. Leave it alone for an hour and it gets bored. Open Spotify and its energy lifts.

### 🍅 Pomodoro Guardian
Pick a focus length (20 / 30 / 45 / 60 / 90 min) in **Settings → ⏰ Reminders** (the tray's *Break Reminders* menu offers Off / 20 / 45 / 60 / 90). The pet counts the time you are *actually* using the PC, then insists on a 10-minute break:

- A chime and a Windows toast announce the break. Then the pet nags every ~90 seconds while you keep working, each time more firmly, with a sound from the second reminder on.
- Time away from the keyboard (no input for 30 s) is added up. Reach 10 minutes and the Pomodoro counts as complete.
- Rest time is never thrown away; only 30 minutes of *ignoring* the break abandons the round.
- Resting 3+ minutes on your own during a focus block resets the focus counter.
- Three reminder styles — **Friendly, Stern, Silly** — flavoured by the pet's own personality.
- **Focus streak** (Pomodoros finished today) and a **7-day productivity report** are shown in Settings, and your daily total appears in *Pet Status*.

### ⏱️ Voice Timers
`"set timer 5 minutes"` starts a real one-shot timer. When it ends the pet rings a melody, shows a long speech bubble, sends a Windows toast and does a trick — then rings again after 20 s and 40 s until you click the pet. `"cancel timer"` stops it.

### 🔊 PC Volume by Voice
`"volume 70"` sets your computer's volume to exactly 70%. Also `"volume up"`, `"volume down"`, `"volume max"`, `"mute"` and `"unmute"`. Works with no Spotify account: install `pycaw` for exact control; without it the pet simulates volume keys (approximate).

### 🎤 Voice Commands
Wake word detection (e.g. "hey dragon") + natural language commands:
- `"play lofi"` — controls Spotify
- `"open chrome"` / `"open youtube"` — launches apps and websites
- `"do a backflip"` — triggers trick animations
- `"set timer 10 minutes"` / `"volume 40"` — timers and PC volume
- `"my name is Alex"` — the pet learns and remembers

See the full list under [Voice Commands](#voice-commands).

### 📖 Memory System
The pet learns facts about you across sessions. Tell it your name, job, where you live, or what you like — it remembers and injects this context (plus your most recent conversation) into every LLM response. Facts you add by hand in the dashboard are used too. The **Pet Memory Dashboard** (Settings → 🧠 Memory) has four tabs:

- **Facts** — what the pet knows about you (add or edit by hand)
- **Apps** — time spent per application
- **Emotions** — recent mood history
- **Stats** — sessions, late-night sessions, most active hours, top apps, recent moods

### 🏆 Achievement System
50+ achievements (51 in total) across 7 categories: Caretaker, Performer, Devoted, Bonded, Explorer, Legend, and Secret. Bronze through Legend tier. The pet notifies you when you unlock one. Trophy wall in Settings shows your full progress.

### 📊 HUD Overlay
Compact 130×42px pill above the pet showing mood emoji, pet type emoji, level, hunger bar (color-coded), XP bar, and streak fire. Auto-hides when nothing urgent. Force-shows after feeding or leveling up. Speech bubbles follow the pet and stay clear of the HUD.

### 🎵 Spotify Integration (optional)
The pet reacts to music. Dance animations when a banger drops. Notifies you when tracks change. Without Spotify API credentials it controls playback with media keys, so `play / pause / skip / next` still work. To enable the full API add `spotify_client_id` and `spotify_client_secret` to `config.json` (see `spotify_api.py`).

### 🌙 Day/Night Awareness
Night tint after 9pm. Different idle animations. Sleepier responses. The pet knows when it's 3am and that you probably shouldn't be awake. It also falls asleep when you go idle (AFK) and greets you when you come back.

### 👀 Context Awareness
Reacts when you switch to a different kind of app, join a meeting, or copy a link, code or an error message. Seasonal events (New Year, Valentine's, St Patrick's, April Fools, Halloween, Christmas, New Year's Eve) bring their own greetings and accessories.

### 🎩 Accessories + Level System
Feed and interact to earn XP. Level up unlocks accessories — hats, glasses, crowns. Accessories are drawn directly onto sprites using Pillow. All level-gated, all unlockable through normal play.

---

## Installation

### Option 1 — Build the .exe

1. Install the requirements (see Option 2) plus `pyinstaller`
2. Run `python make_icon.py` once to generate `icon.ico`
3. Run `build.bat` — the result is `dist\DesktopPet.exe`
4. Put it anywhere you like and double-click to run

No installer. No admin rights needed. See `BuildAndRelease.MD` for details.

### Option 2 — Run from source

**Requirements:** Python 3.10+, Windows 10/11

```bash
cd desktop_multi_pet_git
pip install -r requirements.txt
python main.py
```

**requirements.txt:**
```
pillow>=10.0.0
pystray>=0.19.0
pywin32>=306
psutil>=5.9.0
SpeechRecognition>=3.10.0
pyaudio>=0.2.13
winotify>=1.1.0
pycaw
comtypes
pyinstaller>=6.0.0
```

`pycaw` and `comtypes` are optional (exact PC-volume control). `pyinstaller` is only needed to build the .exe.

### Option 3 — With Ollama (for AI responses)

1. Install [Ollama](https://ollama.ai)
2. Run: `ollama pull gemma2:2b`
3. Start Ollama, then start Desktop Pet
4. The pet will automatically connect

Without Ollama, the pet uses built-in personality-matched responses — still fun, just not generative.

---

## Usage

| Action | How |
|--------|-----|
| Feed pet | Right-click → Feed, or tray menu |
| Do a trick | Double-click pet, or right-click → Do a Trick |
| Give commands | Tray → 💬 Type a Command, or say the wake word |
| Settings | Right-click → Settings, or tray → Settings... |
| Switch pet | Settings → Identity → Pet Type, or tray → Pet Type |
| Pomodoro / break reminders | Settings → ⏰ Reminders, or tray → Break Reminders |
| View achievements | Settings → 🏆 Achievements |
| View memories | Settings → 🧠 Memory |
| Pet status | Right-click → Pet Status |
| Follow cursor / sit | Right-click → Follow Cursor / Sit / Stay |
| Move pet | Click and drag |
| Stop a ringing timer | Click the pet |
| Quit | Right-click → Quit, or tray menu |

Settings has eight tabs: Identity, Appearance, Behaviour (animation speed), Voice (read-only view of the wake words and engine), Reminders (Pomodoro), Memory, Achievements and About. Your settings are written to `config.json` as soon as you change them (the pet's name and personality are kept in its save data).

### Voice Commands

Say the wake word, then your command — in one sentence ("dragon open chrome") or separately (say the wake word, then you have 8 seconds to say the command).

| Pet | Wake words |
|-----|-----------|
| 🐉 Dragon | `hey dragon`, `okay dragon`, `dragon`, `hey buddy` |
| 🐶 Dog | `hey buddy`, `okay dog`, `hey dog`, `hey doug`, `buddy`, `dog` |
| 🐱 Cat | `hey kitty`, `hey cat`, `okay kitty`, `kitty`, `hey buddy`, `cat` |

```
MUSIC
"play [song/artist]"        — Spotify (API if configured, otherwise opens Spotify search)
"pause" / "house" / "stop"  — pause (media key: toggles play/pause without the API)
"resume"                    — play again
"skip" / "next"             — next track

VOLUME (PC volume)
"volume [0-100]"            — set exact volume          "volume max" — 100%
"volume up" / "volume down" — ±10%   (also "louder" / "quieter")
"mute" / "unmute"           — mute the PC
"volume"                    — tells you the current level

OPEN
"open [app name]"           — chrome, firefox, edge, vs code, notepad, calculator,
                              explorer, task manager, slack, terminal,
                              powershell, word, excel, powerpoint, paint, spotify
"open [website]"            — youtube, gmail, google drive, calendar, github
"search [query]"            — Google search in your browser (also "google [query]")

TIMERS
"set timer [N] minutes"     — also seconds / hours, "an hour", "remind me in 2 hours"
"cancel timer"              — stop it

PET
"feed" / "treat" / "bone"   — feed the pet
"trick"                     — random trick; or "jump", "spin", "dance", "roll",
                              "flip", "shake", "moonwalk", "sneeze", "dizzy"
"your name is [name]"       — rename the pet ("call yourself ...", "you are now ...")
anything else               — chat with the pet (it also learns facts about you)
```

Notes: keywords match anywhere in a sentence and music keywords are checked first, so a sentence containing "next" or "stop" is treated as a music command. `"close ..."` is not a command. If the pet has no animation for a trick (for example the dragon's `roll`), it performs a random trick of its own.

---

## Configuration

Settings are stored in `config.json` next to the app and saved immediately when you change something. You can also edit it by hand while the pet is closed.

| Key | Meaning |
|-----|---------|
| `pet` | `dog`, `dragon` or `cat` |
| `speed` | Animation speed (0.3 – 3.0) |
| `color`, `accessory` | Current tint and accessory |
| `last_x`, `last_y` | Last position (refreshed about once a minute and on quit) |
| `reminder_min` | Pomodoro focus length: `0` (off), `20`, `30`, `45`, `60`, `90` |
| `reminder_style` | `friendly`, `stern` or `silly` |
| `hud_enabled` | Show the HUD |
| `wake_words` | The wake words of the **current** pet (informational) |
| `afk_sleep_sec`, `follow_speed` | Seconds idle before the pet sleeps; cursor-follow speed (not shown in Settings) |
| `spotify_client_id`, `spotify_client_secret` | Optional Spotify API credentials |

Other keys you add are preserved. Set the environment variable `PET_VERBOSE=1` to print notices about optional integrations that are switched off.

---

## Architecture

```
main.py              — DesktopPet class, main loop, event wiring
├── pet_state.py     — hunger, XP, level, mood, persistence
├── emotion_engine.py— 2D valence/arousal continuous mood state
├── llm_brain.py     — Ollama integration, fallback pools, command classification
├── memory.py        — persistent facts, exchanges, app time, active hours
├── achievements.py  — 51 achievement definitions and unlock logic
├── behavior.py      — state machine (idle/walk/sleep/trick/follow/curious)
├── reminders.py     — Pomodoro engine (focus/break, nagging, styles)
├── alert_sound.py   — reminder / timer melodies (winsound, no audio files)
├── hud.py           — transparent HUD overlay
├── speech.py        — speech bubble overlay (follows the pet)
├── particles.py     — hearts, stars, zzz, notes, sparkles
├── tray.py          — system tray icon and menu
├── voice.py         — wake word detection, STT, command routing
├── command_handler.py— executes classified commands (music, apps, timers...)
├── system_volume.py — PC volume / mute (pycaw, with media-key fallback)
├── sprite.py        — dog pixel art, 30 animations
├── dragon_sprite.py — dragon pixel art, 24 animations
├── cat_sprite.py    — cat pixel art, 30 animations
├── accessories.py   — hat/glasses/crown rendering on sprites
├── pet_window.py    — transparent always-on-top pet window
├── window_utils.py  — keeps Settings/Memory/Achievements windows below the pet
├── settings_window.py— 8-tab Tkinter settings panel
├── memory_dashboard.py— memory viewer/editor UI (Facts, Apps, Emotions, Stats)
├── achievement_ui.py— trophy wall UI
├── screen_time.py   — streak tracking, daily/weekly stats, Pomodoro history
├── day_night.py     — time awareness, app watching, window detection
├── input_tracker.py — cursor position, taskbar detection, idle time
├── clipboard_watcher.py — reacts to copied links, code and errors
├── notifications.py — Windows toast notifications
├── spotify_api.py   — optional Spotify Web API integration
├── seasonal.py      — holiday greetings, seasonal accessories
├── startup_chooser.py— pet selection on first launch
├── updater.py       — checks GitHub for a newer release
├── make_icon.py     — generates icon.ico for the build
└── config_manager.py— persistent config, works in both source + exe
```

---


## Credits

Built with:
- [Pillow](https://python-pillow.org/) — sprite rendering and compositing
- [pystray](https://github.com/moses-palmer/pystray) — system tray
- [Ollama](https://ollama.ai) — local LLM inference
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) — voice STT
- [winotify](https://github.com/versa-syahptr/winotify) — Windows notifications
- [pycaw](https://github.com/AndreMiras/pycaw) — Windows volume control (optional)

All pixel art hand-crafted in Python using Pillow's `ImageDraw`.

---

## License

MIT — do whatever you want. Attribution appreciated but not required.

---

<div align="center">

**Based on Desktop Pet by [chron303](https://github.com/chron303)**

*"The best products don't just solve problems. They become part of people's lives."*

[⭐ Star the original repo](https://github.com/chron303/desktop-pet) if your pet made you smile today.

</div>
