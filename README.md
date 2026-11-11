# The Matrix – Terminal Text Adventure

A retro terminal-style interactive fiction game built with **Pygame**.

Experience key scenes from *The Matrix* and the beginning of *The Matrix Reloaded* through branching dialogue choices, character portraits, atmospheric music, save/load, volume control, and a resizable window.

---

## Features

- Full first-film path (white rabbit → pills → Oracle → lobby → subway → becoming The One)
- **Reloaded extension**: return to Zion, Seraph, second Oracle meeting, Agent Smith confrontation
- Green-on-black retro aesthetic
- Save / Load progress (`savegame.json`)
- Clickable top menu: **SAVE**, **LOAD**, **EXIT**
- **Volume control**: `M` = mute/unmute, `+` / `-` = volume up/down
- **Resizable window** with letterboxing (keeps correct aspect ratio)
- Flexible input (keyword or number)
- Graceful media fallbacks

---

## Controls

| Action              | Input                          |
|---------------------|--------------------------------|
| Make a choice       | Type keyword or number + ENTER |
| Save                | Click SAVE or use the menu     |
| Load                | Click LOAD                     |
| Exit                | Click EXIT                     |
| Mute / Unmute       | `M`                            |
| Volume up / down    | `+` or `=`  /  `-`             |
| Restart after ending| Any key                        |

---

## Requirements

```bash
pip install -r requirements.txt
```

- Python 3.8+
- pygame >= 2.5
- gif-pygame (optional, for the digital-rain animation)

---

## How to Run

```bash
git clone https://github.com/Mohamadx2/The-matrix-game.git
cd The-matrix-game
pip install -r requirements.txt
python matrix_game.py
```

You can freely resize the window; the game will letterbox to keep the original aspect ratio.

---

## Project Structure

```text
├── matrix_game.py
├── requirements.txt
├── LICENSE
├── README.md
├── savegame.json          # created when you save
└── media/
    ├── Digital_rain.gif
    ├── matrix_theme.mp3
    ├── morpheus.jpg
    └── neo.jpg
```

---

## License

MIT License – see [LICENSE](LICENSE).

*This is an unofficial fan project. All Matrix-related intellectual property belongs to Warner Bros. and the Wachowskis.*
