# 🕶️ The Matrix – Terminal Text Adventure

A retro, terminal-style interactive fiction game built in Python using **Pygame**. Experience the iconic narrative of *The Matrix* through multi-branching dialogue choices, authentic script scenes, atmospheric background audio, dynamic UI windows, and built-in save/load state management.

---

## 📸 Features

* **Authentic Matrix Narrative:** Scripted scenes based on *The Matrix* shooting script, featuring memorable encounters with Trinity, Morpheus, Agent Smith, the Oracle, and Spoon Boy.
* **Retro Terminal UI:** Clean, centered windowed interface designed with green-on-black retro aesthetics, paired character portrait previews, and wrapped multi-line text.
* **Interactive Dialogue System:** Branching choices driving different storylines, leading to unique endings or classic narrative paths.
* **Audio Subsystem:** Seamless background MP3 music streaming via `pygame.mixer` to heighten atmospheric immersion.
* **Save / Load Persistence:** Built-in JSON serialization allowing you to archive progress and restore runtime state at any point via the top navigation menu.
* **Safe Asset Management:** Error-handled media pipeline capable of dynamically loading static images (`.png`/`.jpg`) and animated GIFs (`.gif`).

---

## 🛠️ Requirements & Prerequisites

* **Python 3.8+**
* **Dependencies:**
  * `pygame`
  * `gif-pygame`

Install the required dependencies via `pip`:

```bash
pip install pygame gif-pygame
```

---

## 📁 Repository Structure

```text
├── matrix_game.py          # Main Pygame application & game engine
├── savegame.json           # Auto-generated runtime save state file
├── media/                  # Directory containing media assets
│   ├── matrix_theme.mp3    # Background audio track
│   ├── neo.png             # Character/scene portraits
│   ├── morpheus.jpg
│   ├── red_pill.gif        # Animated terminal assets
│   └── digital_rain.gif
└── README.md               # Project documentation
```

---

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/matrix-text-adventure.git
   cd matrix-text-adventure
   ```

2. **Ensure media assets exist:**
   Place your images (`.png`, `.jpg`, `.gif`) and background music (`matrix_theme.mp3`) in the `media/` folder.

3. **Launch the game:**
   ```bash
   python matrix_game.py
   ```

---

## 🎮 How to Play

1. **Navigation:** Read the narrative text inside the central retro terminal window.
2. **Making Choices:** Type the keyword associated with your desired choice into the command prompt (`> `) at the bottom of the window and press `ENTER`.
3. **Menu Controls (Top Navigation Bar):**
   * Click **SAVE GAME** to save your current progress to disk.
   * Click **LOAD GAME** to restore your saved checkpoint.
   * Click **EXIT** to safely terminate the application.
4. **Restarting:** If you encounter a *GAME OVER* state, press any key to restart from the matrix entry point.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE). 
*Note: Script excerpts and intellectual properties related to "The Matrix" belong to Warner Bros. and Larry & Andy Wachowski.*