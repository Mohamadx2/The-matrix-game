# The Matrix – Terminal Text Adventure

A retro, terminal-style interactive fiction game built with **Pygame**.  
Experience key scenes from *The Matrix* through branching dialogue choices, character portraits, atmospheric music, and a simple save/load system.

---

## Features

- Authentic narrative path covering the main beats of the film (Neo’s awakening, the red/blue pill, the Oracle, the lobby shootout, the subway fight, and becoming The One).
- Green-on-black retro terminal aesthetic with monospace-friendly fonts.
- Character portraits and digital-rain animation.
- Background Matrix-themed music.
- **Save / Load** progress to a local JSON file.
- Top menu bar with clickable **SAVE**, **LOAD**, and **EXIT** buttons.
- Flexible input: type either the keyword (`red`, `club`…) or the number (`1`, `2`).
- Graceful fallbacks when media files are missing.

---

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Project Structure

```text
├── matrix_game.py          # Main game (run this)
├── requirements.txt
├── LICENSE
├── README.md
├── savegame.json           # Created automatically when you save
└── media/
    ├── Digital_rain.gif
    ├── matrix_theme.mp3
    ├── morpheus.jpg
    ├── neo.jpg
    └── null.txt
```

> Note: The older `matrix1.py` is the previous version and can be ignored or deleted.

---

## How to Run

```bash
git clone https://github.com/Mohamadx2/The-matrix-game.git
cd The-matrix-game
pip install -r requirements.txt
python matrix_game.py
```

---

## How to Play

1. Read the narrative text in the main window.
2. Type the **keyword** or the **number** of your choice and press **ENTER**.
3. Use the top bar:
   - **SAVE** – write current progress to `savegame.json`
   - **LOAD** – restore the last saved position
   - **EXIT** – quit the game
4. On a Game Over or Victory screen, press any key to restart from the beginning.

---

## License

This project is released under the [MIT License](LICENSE).

*Script excerpts and intellectual property related to “The Matrix” belong to Warner Bros. and the Wachowskis. This is an unofficial fan project for educational and entertainment purposes only.*
