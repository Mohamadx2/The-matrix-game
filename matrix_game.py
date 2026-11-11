#!/usr/bin/env python3
"""
The Matrix – Terminal Text Adventure
Features: save/load, menu, volume/mute, resizable window (letterbox),
and expanded scenarios from The Matrix + Reloaded.
"""

import pygame
import sys
import os
import json
from pathlib import Path

# Optional GIF support
try:
    import gif_pygame
    HAS_GIF = True
except ImportError:
    HAS_GIF = False
    print("[Notice] gif-pygame not installed. Animated GIFs disabled.")

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
LOGICAL_W, LOGICAL_H = 1050, 750          # fixed logical resolution
SAVE_FILE = "savegame.json"
MEDIA_DIR = Path("media")

# Colours
GREEN = (0, 255, 0)
DARK_GREEN = (0, 120, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)

# ------------------------------------------------------------------
# Initialisation
# ------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

# Start with a resizable window
screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
pygame.display.set_caption("The Matrix – Terminal Text Adventure")
clock = pygame.time.Clock()

# Logical surface we always draw to (keeps aspect ratio)
logical_surface = pygame.Surface((LOGICAL_W, LOGICAL_H))

def get_font(size, bold=False):
    for name in ["Consolas", "Courier New", "DejaVu Sans Mono", "Liberation Mono", "monospace"]:
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)

FONT_LARGE = get_font(32)
FONT_MED = get_font(24)
FONT_SMALL = get_font(18)
FONT_TINY = get_font(16)

# ------------------------------------------------------------------
# Audio + volume control
# ------------------------------------------------------------------
music_volume = 0.35
music_muted = False

def init_background_audio(filepath=MEDIA_DIR / "matrix_theme.mp3"):
    global music_volume
    if filepath.exists():
        try:
            pygame.mixer.music.load(str(filepath))
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            print(f"[Audio Warning] Could not play music: {e}")
    else:
        print(f"[Audio Notice] Music file not found: {filepath}")

def set_volume(vol):
    global music_volume, music_muted
    music_volume = max(0.0, min(1.0, vol))
    if not music_muted:
        pygame.mixer.music.set_volume(music_volume)

def toggle_mute():
    global music_muted
    music_muted = not music_muted
    if music_muted:
        pygame.mixer.music.set_volume(0.0)
        return "Muted"
    else:
        pygame.mixer.music.set_volume(music_volume)
        return f"Unmuted ({int(music_volume*100)}%)"

init_background_audio()

# ------------------------------------------------------------------
# Media helper
# ------------------------------------------------------------------
class Media:
    def __init__(self, path, size=(350, 250), is_gif=False):
        self.path = Path(path)
        self.size = size
        self.is_gif = is_gif and HAS_GIF
        self.asset = None

        if self.path.exists():
            try:
                if self.is_gif:
                    self.asset = gif_pygame.load(str(self.path))
                    self.asset = gif_pygame.transform.scale(self.asset, size)
                else:
                    img = pygame.image.load(str(self.path)).convert_alpha()
                    self.asset = pygame.transform.scale(img, size)
            except Exception as e:
                print(f"[Media Warning] Failed to load {self.path}: {e}")
                self.asset = None
        else:
            print(f"[Media Notice] Missing asset: {self.path}")

    def draw(self, surface, pos):
        if self.asset:
            if self.is_gif:
                self.asset.render(surface, pos)
            else:
                surface.blit(self.asset, pos)
        else:
            rect = pygame.Rect(pos[0], pos[1], self.size[0], self.size[1])
            pygame.draw.rect(surface, DARK_GREEN, rect, 2)
            label = FONT_TINY.render("NO IMAGE", True, DARK_GREEN)
            surface.blit(label, (pos[0] + 10, pos[1] + 10))

# ------------------------------------------------------------------
# Scenario data – original + Reloaded extension
# ------------------------------------------------------------------
SCENARIOS = {
    # ========== ORIGINAL MATRIX ==========
    "start": {
        "text": (
            "You are Neo, a hacker living a double life. A message flashes on your screen:\n"
            "‘Wake up, Neo. The Matrix has you. Follow the white rabbit.’\n\n"
            "Someone knocks on your door. Choi asks you to go out to the club.\n\n"
            "Choices:\n"
            "1. stay  – Stay home and work on your computer.\n"
            "2. club  – Go out to the club with Choi and look for the white rabbit."
        ),
        "options": {"stay": "stay_caught", "club": "club_meet", "1": "stay_caught", "2": "club_meet"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "stay_caught": {
        "text": (
            "You stay home. The next morning Agents arrive at your cubicle. You are captured.\n\n"
            "GAME OVER – Press any key to restart."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "club_meet": {
        "text": (
            "At the club you meet Trinity. The next day Morpheus calls and guides you to escape the Agents.\n\n"
            "Choices:\n"
            "1. scaffold  – Try the scaffolding escape.\n"
            "2. surrender – Give up to Agent Smith."
        ),
        "options": {"scaffold": "interrogation", "surrender": "stay_caught", "1": "interrogation", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "interrogation": {
        "text": (
            "You are captured. Agent Smith implants a bug. You wake up – the phone rings.\n\n"
            "Choices:\n"
            "1. bridge – Answer and meet Morpheus.\n"
            "2. ignore – Stay in bed."
        ),
        "options": {"bridge": "morpheus_meet", "ignore": "stay_caught", "1": "morpheus_meet", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "morpheus_meet": {
        "text": (
            "Morpheus offers the pills.\n\n"
            "Choices:\n"
            "1. red  – Take the red pill.\n"
            "2. blue – Take the blue pill."
        ),
        "options": {"red": "real_world_awakening", "blue": "stay_caught", "1": "real_world_awakening", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "real_world_awakening": {
        "text": (
            "You wake in the real world. After training, Morpheus takes you to the Oracle.\n\n"
            "Choices:\n"
            "1. oracle – Visit the Oracle.\n"
            "2. skip   – Stay on the ship."
        ),
        "options": {"oracle": "oracle_visit", "skip": "building_trap", "1": "oracle_visit", "2": "building_trap"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "oracle_visit": {
        "text": (
            "The Oracle tells you that Morpheus will sacrifice himself for you.\n\n"
            "Choices:\n"
            "1. continue – Accept the path and face the trap.\n"
            "2. deny     – Try to change fate."
        ),
        "options": {"continue": "building_trap", "deny": "building_trap", "1": "building_trap", "2": "building_trap"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "building_trap": {
        "text": (
            "Cypher betrays the crew. Morpheus is captured.\n\n"
            "Choices:\n"
            "1. rescue  – Go in with guns blazing.\n"
            "2. abandon – Leave him behind."
        ),
        "options": {"rescue": "lobby_gunfight", "abandon": "stay_caught", "1": "lobby_gunfight", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "lobby_gunfight": {
        "text": (
            "The lobby shootout and rooftop rescue succeed. You head for the subway.\n\n"
            "Choices:\n"
            "1. subway – Face Agent Smith.\n"
            "2. run    – Try to escape another way."
        ),
        "options": {"subway": "subway_showdown", "run": "stay_caught", "1": "subway_showdown", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "subway_showdown": {
        "text": (
            "Smith kills you. Trinity’s kiss brings you back.\n\n"
            "Choices:\n"
            "1. revive – Become The One.\n"
            "2. die    – Stay dead."
        ),
        "options": {"revive": "hero_victory", "die": "stay_caught", "1": "hero_victory", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "hero_victory": {
        "text": (
            "You destroy Smith from within and free your mind.\n\n"
            "CONGRATULATIONS – End of the first chapter.\n\n"
            "Choices:\n"
            "1. continue – Enter The Matrix Reloaded.\n"
            "2. restart  – Play the first story again."
        ),
        "options": {"continue": "zion_return", "restart": "start", "1": "zion_return", "2": "start"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },

    # ========== MATRIX RELOADED EXTENSION ==========
    "zion_return": {
        "text": (
            "The Nebuchadnezzar returns to Zion. Commander Lock is furious that Morpheus left a ship behind "
            "to wait for the Oracle. The Machines are digging straight toward the city.\n\n"
            "Morpheus still believes the prophecy. He asks one ship to stay near the broadcast level.\n\n"
            "Choices:\n"
            "1. support – Side with Morpheus and prepare to meet the Oracle again.\n"
            "2. lock    – Side with Lock and return fully to Zion."
        ),
        "options": {"support": "seraph_meet", "lock": "zion_stay", "1": "seraph_meet", "2": "zion_stay"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "zion_stay": {
        "text": (
            "You remain in Zion. The Machines continue their advance. Without the Oracle’s guidance "
            "the path of the One remains unclear.\n\n"
            "The story ends here for now.\n\n"
            "Press any key to restart."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "seraph_meet": {
        "text": (
            "You enter the Matrix seeking the Oracle. A man in white awaits you – Seraph.\n\n"
            "Seraph: ‘You seek the Oracle. I can take you to her. But first I must be sure.’\n\n"
            "He attacks. After a short, precise fight he stops.\n\n"
            "Seraph: ‘Good. The Oracle has many enemies. I had to be sure that you are the One.’\n\n"
            "Choices:\n"
            "1. follow – Follow Seraph to the Oracle.\n"
            "2. question – Ask him more about who he is."
        ),
        "options": {"follow": "oracle_reloaded", "question": "oracle_reloaded", "1": "oracle_reloaded", "2": "oracle_reloaded"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "oracle_reloaded": {
        "text": (
            "You find the Oracle on a park bench feeding birds.\n\n"
            "Oracle: ‘Well, come on, I ain’t going to bite you. Come around here and let me have a look at you.’\n\n"
            "She offers you a piece of candy.\n\n"
            "Choices:\n"
            "1. take   – Take the candy.\n"
            "2. refuse – Refuse the candy."
        ),
        "options": {"take": "oracle_candy", "refuse": "oracle_candy", "1": "oracle_candy", "2": "oracle_candy"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "oracle_candy": {
        "text": (
            "Oracle: ‘You’ve already made the choice. You’re here to try to understand why you made it.’\n\n"
            "She tells you that to reach the Source you will need the Keymaker, who is held prisoner by "
            "the Merovingian – an old and dangerous program.\n\n"
            "Oracle: ‘Be there at that exact time and you will have a chance.’\n\n"
            "As she leaves, black birds scatter. A familiar figure approaches.\n\n"
            "Choices:\n"
            "1. face – Stay and face him.\n"
            "2. leave – Try to leave immediately."
        ),
        "options": {"face": "smith_confront", "leave": "smith_confront", "1": "smith_confront", "2": "smith_confront"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "smith_confront": {
        "text": (
            "Agent Smith (no longer an Agent) stands before you.\n\n"
            "Smith: ‘Mister Anderson. Did you get my package?’\n\n"
            "He speaks of purpose, of being unplugged because of you, and of the connection between you.\n\n"
            "More Smiths begin to appear.\n\n"
            "Choices:\n"
            "1. fight – Stand and fight the multiplying Smiths.\n"
            "2. fly   – Attempt to fly away immediately."
        ),
        "options": {"fight": "smith_fight", "fly": "smith_escape", "1": "smith_fight", "2": "smith_escape"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "smith_fight": {
        "text": (
            "The Smiths swarm you. One sinks his fingers into your chest, trying to overwrite you.\n\n"
            "With a surge of will you tear free. You fight, using a fence post as a weapon, but more keep coming.\n\n"
            "Smith: ‘It is… inevitable.’\n\n"
            "You leap into the sky, dragging a chain of Smiths with you.\n\n"
            "You break free and escape – for now.\n\n"
            "The path to the Keymaker and the Merovingian still lies ahead.\n\n"
            "CHAPTER COMPLETE – More of Reloaded can be added later.\n\n"
            "Press any key to restart."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "smith_escape": {
        "text": (
            "You rocket into the sky before the first Smith can connect.\n\n"
            "Behind you the park fills with copies. Smith’s voice echoes:\n\n"
            "‘It is inevitable.’\n\n"
            "You have bought time, but the connection remains.\n\n"
            "CHAPTER COMPLETE – The road to the Merovingian and the Keymaker awaits.\n\n"
            "Press any key to restart."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    }
}

# ------------------------------------------------------------------
# Game state
# ------------------------------------------------------------------
current_scenario = "start"
input_text = ""
restart_pending = False
status_message = ""
status_timer = 0

# Menu buttons (logical coordinates)
BUTTON_H = 32
BUTTON_Y = 8
btn_save = pygame.Rect(20, BUTTON_Y, 110, BUTTON_H)
btn_load = pygame.Rect(140, BUTTON_Y, 110, BUTTON_H)
btn_exit = pygame.Rect(260, BUTTON_Y, 90, BUTTON_H)

def set_status(msg, duration=90):
    global status_message, status_timer
    status_message = msg
    status_timer = duration

def save_game():
    data = {"scenario": current_scenario}
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        set_status("Game saved.")
    except Exception as e:
        set_status(f"Save failed: {e}")

def load_game():
    global current_scenario, input_text, restart_pending
    if not os.path.exists(SAVE_FILE):
        set_status("No save file found.")
        return
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sc = data.get("scenario", "start")
        if sc in SCENARIOS:
            current_scenario = sc
            input_text = ""
            restart_pending = not bool(SCENARIOS[sc]["options"])
            set_status("Game loaded.")
        else:
            set_status("Save file corrupted.")
    except Exception as e:
        set_status(f"Load failed: {e}")

def reset_game():
    global current_scenario, input_text, restart_pending
    current_scenario = "start"
    input_text = ""
    restart_pending = False
    set_status("Restarted.")

def draw_text_wrapped(surface, text, font, colour, x, y, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test = line + word + " "
            if font.size(test)[0] < max_width:
                line = test
            else:
                lines.append(line.rstrip())
                line = word + " "
        lines.append(line.rstrip())

    for line in lines:
        surf = font.render(line, True, colour)
        surface.blit(surf, (x, y))
        y += font.get_linesize() + 2
    return y

def draw_button(surface, rect, label, hover=False):
    colour = DARK_GREEN if hover else GRAY
    pygame.draw.rect(surface, colour, rect, border_radius=4)
    pygame.draw.rect(surface, GREEN, rect, 1, border_radius=4)
    text = FONT_SMALL.render(label, True, GREEN)
    text_rect = text.get_rect(center=rect.center)
    surface.blit(text, text_rect)

def get_scaled_mouse(pos, window_size):
    """Convert real window mouse coordinates to logical coordinates."""
    win_w, win_h = window_size
    scale = min(win_w / LOGICAL_W, win_h / LOGICAL_H)
    offset_x = (win_w - LOGICAL_W * scale) / 2
    offset_y = (win_h - LOGICAL_H * scale) / 2
    if scale == 0:
        return (0, 0)
    lx = (pos[0] - offset_x) / scale
    ly = (pos[1] - offset_y) / scale
    return (lx, ly)

# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
running = True
while running:
    window_size = screen.get_size()
    raw_mouse = pygame.mouse.get_pos()
    mouse_pos = get_scaled_mouse(raw_mouse, window_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            # Window was resized – keep it resizable
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_save.collidepoint(mouse_pos):
                save_game()
            elif btn_load.collidepoint(mouse_pos):
                load_game()
            elif btn_exit.collidepoint(mouse_pos):
                running = False

        elif event.type == pygame.KEYDOWN:
            # Volume / mute controls (always available)
            if event.key == pygame.K_m:
                msg = toggle_mute()
                set_status(msg)
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                set_volume(music_volume + 0.05)
                set_status(f"Volume {int(music_volume*100)}%")
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                set_volume(music_volume - 0.05)
                set_status(f"Volume {int(music_volume*100)}%")

            elif restart_pending:
                reset_game()
            elif event.key == pygame.K_RETURN:
                scenario = SCENARIOS[current_scenario]
                if scenario["options"]:
                    choice = input_text.strip().lower()
                    if choice in scenario["options"]:
                        current_scenario = scenario["options"][choice]
                        input_text = ""
                        if not SCENARIOS[current_scenario]["options"]:
                            restart_pending = True
                    else:
                        set_status("Invalid choice. Type a keyword or number.")
                        input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if not restart_pending and SCENARIOS[current_scenario]["options"]:
                    if event.unicode and event.unicode.isprintable():
                        input_text += event.unicode

    if status_timer > 0:
        status_timer -= 1
        if status_timer == 0:
            status_message = ""

    # --------------------------------------------------------------
    # Draw everything to the logical surface
    # --------------------------------------------------------------
    logical_surface.fill(BLACK)
    scenario = SCENARIOS[current_scenario]

    # Top bar
    pygame.draw.rect(logical_surface, (15, 15, 15), (0, 0, LOGICAL_W, 48))
    pygame.draw.line(logical_surface, DARK_GREEN, (0, 48), (LOGICAL_W, 48), 1)

    draw_button(logical_surface, btn_save, "SAVE", btn_save.collidepoint(mouse_pos))
    draw_button(logical_surface, btn_load, "LOAD", btn_load.collidepoint(mouse_pos))
    draw_button(logical_surface, btn_exit, "EXIT", btn_exit.collidepoint(mouse_pos))

    if status_message:
        status_surf = FONT_TINY.render(status_message, True, GREEN)
        logical_surface.blit(status_surf, (LOGICAL_W - status_surf.get_width() - 20, 14))

    # Media
    media = scenario.get("media")
    media_x = LOGICAL_W - 380
    media_y = 70
    if media:
        media.draw(logical_surface, (media_x, media_y))

    # Text
    text_x = 30
    text_y = 70
    text_width = media_x - 60 if media else LOGICAL_W - 60
    new_y = draw_text_wrapped(logical_surface, scenario["text"], FONT_MED, GREEN, text_x, text_y, text_width)

    # Input / restart
    if scenario["options"] and not restart_pending:
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 else " "
        prompt = "> " + input_text + cursor
        prompt_surf = FONT_LARGE.render(prompt, True, WHITE)
        logical_surface.blit(prompt_surf, (text_x, new_y + 25))
    elif restart_pending:
        msg = FONT_LARGE.render("Press any key to restart", True, WHITE)
        logical_surface.blit(msg, (text_x, new_y + 25))

    # Footer
    hint = FONT_TINY.render(
        "Type keyword/number + ENTER  |  M = mute  +/- = volume  |  SAVE / LOAD / EXIT",
        True, LIGHT_GRAY
    )
    logical_surface.blit(hint, (30, LOGICAL_H - 28))

    # --------------------------------------------------------------
    # Scale logical surface to window with letterboxing
    # --------------------------------------------------------------
    win_w, win_h = window_size
    scale = min(win_w / LOGICAL_W, win_h / LOGICAL_H)
    scaled_w = int(LOGICAL_W * scale)
    scaled_h = int(LOGICAL_H * scale)
    offset_x = (win_w - scaled_w) // 2
    offset_y = (win_h - scaled_h) // 2

    screen.fill(BLACK)
    if scale > 0:
        scaled = pygame.transform.smoothscale(logical_surface, (scaled_w, scaled_h))
        screen.blit(scaled, (offset_x, offset_y))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
