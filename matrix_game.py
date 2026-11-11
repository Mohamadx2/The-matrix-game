#!/usr/bin/env python3
"""
The Matrix – Terminal Text Adventure
Full original story + expanded Matrix Reloaded path
(Merovingian, Persephone, Keymaker, chateau, freeway).
"""

import pygame
import sys
import os
import json
from pathlib import Path

try:
    import gif_pygame
    HAS_GIF = True
except ImportError:
    HAS_GIF = False
    print("[Notice] gif-pygame not installed. Animated GIFs disabled.")

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
LOGICAL_W, LOGICAL_H = 1050, 750
SAVE_FILE = "savegame.json"
MEDIA_DIR = Path("media")

GREEN = (0, 255, 0)
DARK_GREEN = (0, 120, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
pygame.display.set_caption("The Matrix – Terminal Text Adventure")
clock = pygame.time.Clock()
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
# Audio
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
            print(f"[Audio Warning] {e}")
    else:
        print(f"[Audio Notice] Music not found: {filepath}")

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
# Media
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
                print(f"[Media Warning] {self.path}: {e}")
        else:
            print(f"[Media Notice] Missing: {self.path}")

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
# SCENARIOS – Original + full Reloaded extension
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
        "text": "You stay home. Agents capture you.\n\nGAME OVER – Press any key to restart.",
        "options": {},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "club_meet": {
        "text": (
            "At the club you meet Trinity. The next day Morpheus calls and guides you to escape.\n\n"
            "Choices:\n1. scaffold – Try the scaffolding escape.\n2. surrender – Give up to Agent Smith."
        ),
        "options": {"scaffold": "interrogation", "surrender": "stay_caught", "1": "interrogation", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "interrogation": {
        "text": (
            "You are captured. Smith implants a bug. You wake up – the phone rings.\n\n"
            "Choices:\n1. bridge – Answer and meet Morpheus.\n2. ignore – Stay in bed."
        ),
        "options": {"bridge": "morpheus_meet", "ignore": "stay_caught", "1": "morpheus_meet", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "morpheus_meet": {
        "text": (
            "Morpheus offers the pills.\n\n"
            "Choices:\n1. red  – Take the red pill.\n2. blue – Take the blue pill."
        ),
        "options": {"red": "real_world_awakening", "blue": "stay_caught", "1": "real_world_awakening", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "real_world_awakening": {
        "text": (
            "You wake in the real world. After training, Morpheus takes you to the Oracle.\n\n"
            "Choices:\n1. oracle – Visit the Oracle.\n2. skip   – Stay on the ship."
        ),
        "options": {"oracle": "oracle_visit", "skip": "building_trap", "1": "oracle_visit", "2": "building_trap"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "oracle_visit": {
        "text": (
            "The Oracle tells you that Morpheus will sacrifice himself for you.\n\n"
            "Choices:\n1. continue – Accept the path.\n2. deny     – Try to change fate."
        ),
        "options": {"continue": "building_trap", "deny": "building_trap", "1": "building_trap", "2": "building_trap"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "building_trap": {
        "text": (
            "Cypher betrays the crew. Morpheus is captured.\n\n"
            "Choices:\n1. rescue  – Go in with guns blazing.\n2. abandon – Leave him behind."
        ),
        "options": {"rescue": "lobby_gunfight", "abandon": "stay_caught", "1": "lobby_gunfight", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "lobby_gunfight": {
        "text": (
            "The lobby shootout and rooftop rescue succeed. You head for the subway.\n\n"
            "Choices:\n1. subway – Face Agent Smith.\n2. run    – Try another way."
        ),
        "options": {"subway": "subway_showdown", "run": "stay_caught", "1": "subway_showdown", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "subway_showdown": {
        "text": (
            "Smith kills you. Trinity’s kiss brings you back.\n\n"
            "Choices:\n1. revive – Become The One.\n2. die    – Stay dead."
        ),
        "options": {"revive": "hero_victory", "die": "stay_caught", "1": "hero_victory", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "hero_victory": {
        "text": (
            "You destroy Smith from within and free your mind.\n\n"
            "CONGRATULATIONS – End of the first chapter.\n\n"
            "Choices:\n1. continue – Enter The Matrix Reloaded.\n2. restart  – Play the first story again."
        ),
        "options": {"continue": "zion_return", "restart": "start", "1": "zion_return", "2": "start"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },

    # ========== RELOADED – EARLY ==========
    "zion_return": {
        "text": (
            "The Nebuchadnezzar returns to Zion. Commander Lock is furious. The Machines are digging "
            "straight toward the city. Morpheus still believes the prophecy and wants a ship near "
            "the broadcast level in case the Oracle calls.\n\n"
            "Choices:\n1. support – Side with Morpheus.\n2. lock    – Side with Lock and stay in Zion."
        ),
        "options": {"support": "seraph_meet", "lock": "zion_stay", "1": "seraph_meet", "2": "zion_stay"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "zion_stay": {
        "text": "You remain in Zion. Without the Oracle the path stays unclear.\n\nPress any key to restart.",
        "options": {},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "seraph_meet": {
        "text": (
            "You enter the Matrix seeking the Oracle. A man in white awaits – Seraph.\n\n"
            "Seraph: ‘You seek the Oracle. I can take you to her. But first I must be sure.’\n\n"
            "After a short fight he stops: ‘Good. The Oracle has many enemies. I had to be sure that you are the One.’\n\n"
            "Choices:\n1. follow – Follow Seraph.\n2. question – Ask who he is."
        ),
        "options": {"follow": "oracle_reloaded", "question": "oracle_reloaded", "1": "oracle_reloaded", "2": "oracle_reloaded"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "oracle_reloaded": {
        "text": (
            "The Oracle sits on a park bench feeding birds.\n\n"
            "Oracle: ‘Well, come on, I ain’t going to bite you.’ She offers candy.\n\n"
            "Choices:\n1. take   – Take the candy.\n2. refuse – Refuse it."
        ),
        "options": {"take": "oracle_candy", "refuse": "oracle_candy", "1": "oracle_candy", "2": "oracle_candy"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "oracle_candy": {
        "text": (
            "Oracle: ‘You’ve already made the choice. You’re here to understand why.’\n\n"
            "She tells you that to reach the Source you need the Keymaker, held by the Merovingian – "
            "one of the oldest and most dangerous programs.\n\n"
            "As she leaves, black birds scatter. A familiar figure approaches.\n\n"
            "Choices:\n1. face – Stay and face him.\n2. leave – Try to leave."
        ),
        "options": {"face": "smith_confront", "leave": "smith_confront", "1": "smith_confront", "2": "smith_confront"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "smith_confront": {
        "text": (
            "Agent Smith (no longer an Agent) stands before you.\n\n"
            "Smith: ‘Mister Anderson. Did you get my package?’\n\n"
            "He speaks of purpose and the connection between you. More Smiths begin to appear.\n\n"
            "Choices:\n1. fight – Stand and fight.\n2. fly   – Attempt to escape into the sky."
        ),
        "options": {"fight": "smith_fight", "fly": "smith_escape", "1": "smith_fight", "2": "smith_escape"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "smith_fight": {
        "text": (
            "The Smiths swarm you. One sinks fingers into your chest. With a surge of will you tear free, "
            "fight, then leap into the sky dragging a chain of them.\n\n"
            "You break free – for now. The path to the Keymaker still lies ahead.\n\n"
            "Choices:\n1. continue – Seek the Merovingian.\n2. rest     – Return to the ship for now."
        ),
        "options": {"continue": "merovingian_restaurant", "rest": "zion_return", "1": "merovingian_restaurant", "2": "zion_return"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "smith_escape": {
        "text": (
            "You rocket into the sky before the first Smith can connect.\n\n"
            "Smith’s voice echoes: ‘It is inevitable.’\n\n"
            "You have bought time. The road to the Merovingian awaits.\n\n"
            "Choices:\n1. continue – Seek the Merovingian.\n2. rest     – Return to the ship."
        ),
        "options": {"continue": "merovingian_restaurant", "rest": "zion_return", "1": "merovingian_restaurant", "2": "zion_return"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },

    # ========== MEROVINGIAN / PERSEPHONE / KEYMAKER ==========
    "merovingian_restaurant": {
        "text": (
            "You, Morpheus and Trinity enter Le Vrai, an exclusive French restaurant high above the city.\n\n"
            "The Merovingian greets you with a razor-thin smile and a French accent.\n\n"
            "Merovingian: ‘Here he is at last – Neo, the One himself. And the legendary Morpheus. "
            "And of course Trinity, so beautiful it causes me to suffer pain.’\n\n"
            "He speaks of causality: ‘There is only one constant… Action, reaction. Cause and effect. "
            "Choice is an illusion created between those with power and those without.’\n\n"
            "Choices:\n1. demand – Demand the Keymaker.\n2. listen – Let him finish his speech."
        ),
        "options": {"demand": "merovingian_refuse", "listen": "merovingian_refuse", "1": "merovingian_refuse", "2": "merovingian_refuse"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250))
    },
    "merovingian_refuse": {
        "text": (
            "Merovingian: ‘The Keymaker is mine. I see no reason to give him up. No reason at all.’\n\n"
            "He leaves. His men surround you. Then the elevator opens and Persephone stands there.\n\n"
            "Persephone: ‘If you want the Keymaker, follow me.’\n\n"
            "Choices:\n1. follow – Follow Persephone.\n2. stay   – Refuse and fight the guards."
        ),
        "options": {"follow": "persephone_lead", "stay": "stay_caught", "1": "persephone_lead", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "persephone_lead": {
        "text": (
            "Persephone leads you through the chateau. In the library she calmly shoots one of her "
            "husband’s old Exiles with a silver bullet.\n\n"
            "Persephone: ‘I am so sick of his bullshit. A long time ago he was different… like you.’\n\n"
            "She opens a hidden door into a medieval basement filled with keys.\n\n"
            "An older Japanese man looks up from his work.\n\n"
            "Keymaker: ‘Yes. I am the Keymaker. I have been waiting for you.’\n\n"
            "Choices:\n1. take – Take the Keymaker and leave.\n2. talk – Ask him about the Source."
        ),
        "options": {"take": "chateau_fight", "talk": "chateau_fight", "1": "chateau_fight", "2": "chateau_fight"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "chateau_fight": {
        "text": (
            "The Merovingian and his men burst into the great hall.\n\n"
            "Merovingian: ‘My God! Persephone! How could you do this!’\n\n"
            "Persephone: ‘Cause and effect, my love. How about the lipstick you’re still wearing?’\n\n"
            "She walks out. The Twins phase through the floor. Neo holds the hall while Morpheus and "
            "Trinity race after the Keymaker into the underground garage.\n\n"
            "Choices:\n1. hold – Hold the hall and cover the escape.\n2. chase – Chase after the Keymaker yourself."
        ),
        "options": {"hold": "freeway_start", "chase": "freeway_start", "1": "freeway_start", "2": "freeway_start"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },

    # ========== FREEWAY ==========
    "freeway_start": {
        "text": (
            "Trinity and Morpheus escape in one of the Merovingian’s cars with the Keymaker. "
            "The Twins pursue. Agents are also closing in.\n\n"
            "You are still in the mountains after the Merovingian slammed a door that exited "
            "into another part of the Matrix. Link tells you where the chase is heading.\n\n"
            "Choices:\n1. intercept – Fly to the freeway and intercept.\n2. trust     – Trust Trinity and Morpheus to handle it."
        ),
        "options": {"intercept": "freeway_fight", "trust": "freeway_fight", "1": "freeway_fight", "2": "freeway_fight"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    },
    "freeway_fight": {
        "text": (
            "The freeway is chaos. Agents, the Twins, trucks, motorcycles. Trinity drives like a "
            "woman possessed while Morpheus fights on the moving vehicles.\n\n"
            "You arrive in time. The Keymaker is nearly lost several times. In the end you, "
            "Trinity, Morpheus and the Keymaker make it off the freeway alive.\n\n"
            "The Keymaker looks at you.\n\n"
            "Keymaker: ‘There is a building. Inside this building there is a level where no elevator can go, "
            "and no stair can reach. This level is filled with doors. These doors lead to many places… "
            "hidden places. One door leads to the Source.’\n\n"
            "Choices:\n1. source – Begin the journey to the Source.\n2. rest   – Return to Zion first."
        ),
        "options": {"source": "keymaker_plan", "rest": "zion_return", "1": "keymaker_plan", "2": "zion_return"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "keymaker_plan": {
        "text": (
            "The Keymaker explains the back-door system and the window of opportunity that opens "
            "only for a few minutes every 107 minutes when the security system resets.\n\n"
            "Keymaker: ‘The door must be opened while the system is resetting. Only then can the door "
            "be opened. Only then can the One reach the Source.’\n\n"
            "You now have the Keymaker and the plan. The final approach to the Source still lies ahead.\n\n"
            "CHAPTER COMPLETE – You have the Keymaker.\n\n"
            "Press any key to restart, or continue expanding the story later."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250))
    }
}

# ------------------------------------------------------------------
# Game state & helpers
# ------------------------------------------------------------------
current_scenario = "start"
input_text = ""
restart_pending = False
status_message = ""
status_timer = 0

btn_save = pygame.Rect(20, 8, 110, 32)
btn_load = pygame.Rect(140, 8, 110, 32)
btn_exit = pygame.Rect(260, 8, 90, 32)

def set_status(msg, duration=90):
    global status_message, status_timer
    status_message = msg
    status_timer = duration

def save_game():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"scenario": current_scenario}, f, indent=2)
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
    surface.blit(text, text.get_rect(center=rect.center))

def get_scaled_mouse(pos, window_size):
    win_w, win_h = window_size
    scale = min(win_w / LOGICAL_W, win_h / LOGICAL_H)
    offset_x = (win_w - LOGICAL_W * scale) / 2
    offset_y = (win_h - LOGICAL_H * scale) / 2
    if scale == 0:
        return (0, 0)
    return ((pos[0] - offset_x) / scale, (pos[1] - offset_y) / scale)

# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
running = True
while running:
    window_size = screen.get_size()
    mouse_pos = get_scaled_mouse(pygame.mouse.get_pos(), window_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_save.collidepoint(mouse_pos):
                save_game()
            elif btn_load.collidepoint(mouse_pos):
                load_game()
            elif btn_exit.collidepoint(mouse_pos):
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                set_status(toggle_mute())
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

    # Draw to logical surface
    logical_surface.fill(BLACK)
    scenario = SCENARIOS[current_scenario]

    pygame.draw.rect(logical_surface, (15, 15, 15), (0, 0, LOGICAL_W, 48))
    pygame.draw.line(logical_surface, DARK_GREEN, (0, 48), (LOGICAL_W, 48), 1)
    draw_button(logical_surface, btn_save, "SAVE", btn_save.collidepoint(mouse_pos))
    draw_button(logical_surface, btn_load, "LOAD", btn_load.collidepoint(mouse_pos))
    draw_button(logical_surface, btn_exit, "EXIT", btn_exit.collidepoint(mouse_pos))

    if status_message:
        status_surf = FONT_TINY.render(status_message, True, GREEN)
        logical_surface.blit(status_surf, (LOGICAL_W - status_surf.get_width() - 20, 14))

    media = scenario.get("media")
    media_x = LOGICAL_W - 380
    if media:
        media.draw(logical_surface, (media_x, 70))

    text_width = media_x - 60 if media else LOGICAL_W - 60
    new_y = draw_text_wrapped(logical_surface, scenario["text"], FONT_MED, GREEN, 30, 70, text_width)

    if scenario["options"] and not restart_pending:
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 else " "
        prompt_surf = FONT_LARGE.render("> " + input_text + cursor, True, WHITE)
        logical_surface.blit(prompt_surf, (30, new_y + 25))
    elif restart_pending:
        logical_surface.blit(FONT_LARGE.render("Press any key to restart", True, WHITE), (30, new_y + 25))

    hint = FONT_TINY.render("Type keyword/number + ENTER  |  M = mute  +/- = volume  |  SAVE / LOAD / EXIT", True, LIGHT_GRAY)
    logical_surface.blit(hint, (30, LOGICAL_H - 28))

    # Letterbox scale
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
