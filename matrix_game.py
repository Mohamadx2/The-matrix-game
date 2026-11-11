#!/usr/bin/env python3
"""
The Matrix – Terminal Text Adventure
Improved version with save/load, menu buttons, fixed assets, and cleaner structure.
"""

import pygame
import sys
import os
import json
import textwrap
from pathlib import Path

# Optional GIF support
try:
    import gif_pygame
    HAS_GIF = True
except ImportError:
    HAS_GIF = False
    print("[Notice] gif-pygame not installed. Animated GIFs will be disabled.")

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
SCREEN_W, SCREEN_H = 1050, 750
SAVE_FILE = "savegame.json"
MEDIA_DIR = Path("media")

# Colours
GREEN = (0, 255, 0)
DARK_GREEN = (0, 120, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
RED = (220, 50, 50)

# ------------------------------------------------------------------
# Initialisation
# ------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("The Matrix – Terminal Text Adventure")
clock = pygame.time.Clock()

# Fonts (prefer monospace if available, otherwise default)
def get_font(size, bold=False):
    # Try common monospace fonts first for a more "terminal" feel
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
def init_background_audio(filepath=MEDIA_DIR / "matrix_theme.mp3"):
    if filepath.exists():
        try:
            pygame.mixer.music.load(str(filepath))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            print(f"[Audio Warning] Could not play music: {e}")
    else:
        print(f"[Audio Notice] Music file not found: {filepath}")

init_background_audio()

# ------------------------------------------------------------------
# Media helper
# ------------------------------------------------------------------
class Media:
    """Safe loader for still images or animated GIFs with fallback."""

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
            # Simple fallback rectangle + label
            rect = pygame.Rect(pos[0], pos[1], self.size[0], self.size[1])
            pygame.draw.rect(surface, DARK_GREEN, rect, 2)
            label = FONT_TINY.render("NO IMAGE", True, DARK_GREEN)
            surface.blit(label, (pos[0] + 10, pos[1] + 10))

# ------------------------------------------------------------------
# Scenario data (cleaned, fixed paths)
# ------------------------------------------------------------------
# Note: Digital_rain.gif has capital D; neo.jpg / morpheus.jpg exist.
# red_pill.gif does not exist → we reuse the rain GIF.

SCENARIOS = {
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
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250), is_gif=False)
    },
    "stay_caught": {
        "text": (
            "You stay home. The next morning at Meta CorTechs, Rhineheart warns you about your attitude. "
            "Shortly after, Agents arrive at your cubicle. You are captured and brought in for interrogation.\n\n"
            "GAME OVER – Press any key to restart."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "club_meet": {
        "text": (
            "At the club, you notice a woman with a small white rabbit tattoo on her jacket: Trinity. "
            "She approaches you and whispers:\n"
            "‘The answer is out there, Neo. It's looking for you and it will find you, if you want it to.’\n\n"
            "The next day at work, a FedEx package arrives containing a cell phone. Morpheus calls you, guiding you to escape the Agents.\n\n"
            "Choices:\n"
            "1. scaffold  – Try to escape across the dangerous building scaffolding.\n"
            "2. surrender – Give up and surrender to Agent Smith."
        ),
        "options": {"scaffold": "interrogation", "surrender": "stay_caught", "1": "interrogation", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "interrogation": {
        "text": (
            "You attempt the escape, but slip and get captured by the Agents. "
            "In the interrogation room, Agent Smith slides a file across the table and says:\n"
            "‘We are willing to wipe the slate clean... all we are asking in return is your cooperation in bringing a known terrorist to justice... Morpheus.’\n\n"
            "Neo: ‘How about I just give you the finger... And you give me my phone call!’\n"
            "Smith seals your mouth shut and implants a horrific bug into your stomach. "
            "You wake up in bed—was it a dream? The phone rings.\n\n"
            "Choices:\n"
            "1. bridge – Answer the phone and agree to meet Morpheus at the Adams Street bridge.\n"
            "2. ignore – Ignore the call and stay in bed."
        ),
        "options": {"bridge": "morpheus_meet", "ignore": "stay_caught", "1": "morpheus_meet", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "Digital_rain.gif", (400, 300), is_gif=True)
    },
    "morpheus_meet": {
        "text": (
            "Trinity and her crew pick you up, extract the bug from your stomach, and bring you to Room 1313 to meet Morpheus.\n"
            "Morpheus: ‘You have the look of a man who accepts what he sees because he is expecting to wake up... "
            "Unfortunately, no one can be told what the Matrix is. You have to see it for yourself.’\n\n"
            "He opens his hands: ‘This is your last chance. After this, there is no going back.’\n\n"
            "Choices:\n"
            "1. red  – Take the red pill and discover the truth of the desert of the real.\n"
            "2. blue – Take the blue pill and wake up in your bed believing whatever you want."
        ),
        "options": {"red": "real_world_awakening", "blue": "stay_caught", "1": "real_world_awakening", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250), is_gif=False)
    },
    "real_world_awakening": {
        "text": (
            "You wake up naked and slimy inside a liquid-filled pod, a cable plugged directly into the back of your skull. "
            "You are rescued by the Nebuchadnezzar hovercraft. Morpheus welcomes you to the real world. "
            "After recovering, you undergo intense combat loading programs (Jujitsu, Kung Fu) and jump training.\n\n"
            "Next, Morpheus takes you to visit the Oracle to find your path.\n\n"
            "Choices:\n"
            "1. oracle – Meet the Oracle and the Spoon Boy in her kitchen.\n"
            "2. skip   – Skip the Oracle visit and stay on the ship."
        ),
        "options": {"oracle": "oracle_visit", "skip": "building_trap", "1": "oracle_visit", "2": "building_trap"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250), is_gif=False)
    },
    "oracle_visit": {
        "text": (
            "Inside the Oracle's apartment, a Spoon Boy hands you a spoon and tells you: "
            "‘Do not try to bend the spoon. That is impossible. Instead, only try to realize the truth... There is no spoon.’\n\n"
            "The Oracle bakes cookies and tells you your fortune:\n"
            "‘Sorry, kid. You got the gift, but looks like you're waiting for something... Your next life, maybe.’\n"
            "She warns you that Morpheus will sacrifice his life to save yours, forcing you to choose between your life and his.\n\n"
            "Choices:\n"
            "1. betrayal – Cypher betrays the crew to the Agents at the hotel trap.\n"
            "2. fight    – Stand your ground against Agent Smith in the building walls."
        ),
        "options": {"betrayal": "building_trap", "fight": "building_trap", "1": "building_trap", "2": "building_trap"},
        "media": Media(MEDIA_DIR / "morpheus.jpg", (350, 250), is_gif=False)
    },
    "building_trap": {
        "text": (
            "A trap springs! Cypher's betrayal leads the Agents straight to you. Mouse is killed, and Morpheus allows himself to be captured by Agent Smith to protect Neo.\n\n"
            "Tank tells the team that Morpheus will soon break under interrogation and give up the mainframe access codes to Zion.\n"
            "Neo refuses to abandon Morpheus: ‘I'm going in... I believe I can bring him back.’\n\n"
            "Choices:\n"
            "1. rescue  – Load up with 'Lots of guns' and launch a suicidal rescue mission on the government building.\n"
            "2. abandon – Leave Morpheus behind and accept Zion's destruction."
        ),
        "options": {"rescue": "lobby_gunfight", "abandon": "stay_caught", "1": "lobby_gunfight", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250), is_gif=False)
    },
    "lobby_gunfight": {
        "text": (
            "You and Trinity burst through the revolving doors of the government building. "
            "Security guard: ‘Would you please remove any metallic items you are carrying...’\n"
            "You open your trench coat, revealing an overwhelming arsenal, and execute a breathtaking lobby shootout. "
            "You scale the elevator shaft, blow the cables, and make it to the rooftop where you face Agent Jones in slow-motion Bullet-Time!\n\n"
            "Trinity saves the day: ‘Dodge this!’ You pilot a B-212 military helicopter straight into the executive office to rescue Morpheus.\n\n"
            "Choices:\n"
            "1. subway          – Escape through the subway station where Agent Smith waits for you.\n"
            "2. surrender_agent – Surrender to Agent Smith."
        ),
        "options": {"subway": "subway_showdown", "surrender_agent": "stay_caught", "1": "subway_showdown", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250), is_gif=False)
    },
    "subway_showdown": {
        "text": (
            "At the subway station, Agent Smith confronts you.\n"
            "Smith: ‘I'm going to enjoy watching you die, Mr. Anderson.’\n"
            "After a brutal clash on the tracks, an oncoming train strikes Smith. You flee through the city alleys toward room 303. "
            "Tragically, Agent Smith ambushes you at the door and shoots you dead.\n\n"
            "Back on the hovercraft, Trinity refuses to accept your death:\n"
            "‘You can't be dead, Neo, you can't be because I love you... I love you!’ She kisses you.\n\n"
            "Choices:\n"
            "1. revive    – Your eyes snap open. You are truly becoming The One.\n"
            "2. stay_dead – Stay dead and let the machines win."
        ),
        "options": {"revive": "hero_victory", "stay_dead": "stay_caught", "1": "hero_victory", "2": "stay_caught"},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250), is_gif=False)
    },
    "hero_victory": {
        "text": (
            "You stand up. The bullets fired by the Agents freeze in mid-air and drop harmlessly to the floor. "
            "You see through the code of the Matrix, thrust your hand into Agent Smith, and destroy him from within!\n\n"
            "CONGRATULATIONS – You have liberated your mind, saved Morpheus, and become the hero of the Matrix!\n\n"
            "Press any key to restart."
        ),
        "options": {},
        "media": Media(MEDIA_DIR / "neo.jpg", (350, 250), is_gif=False)
    }
}

# ------------------------------------------------------------------
# Game state
# ------------------------------------------------------------------
current_scenario = "start"
input_text = ""
restart_pending = False
status_message = ""          # temporary feedback ("Game saved", "Invalid choice", etc.)
status_timer = 0

# Menu button rectangles (top bar)
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

def draw_text_wrapped(text, font, colour, x, y, max_width):
    """Draw multi-line text with word wrapping. Returns the y after the last line."""
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
        screen.blit(surf, (x, y))
        y += font.get_linesize() + 2
    return y

def draw_button(rect, label, hover=False):
    colour = DARK_GREEN if hover else GRAY
    pygame.draw.rect(screen, colour, rect, border_radius=4)
    pygame.draw.rect(screen, GREEN, rect, 1, border_radius=4)
    text = FONT_SMALL.render(label, True, GREEN)
    text_rect = text.get_rect(center=rect.center)
    screen.blit(text, text_rect)

# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_save.collidepoint(mouse_pos):
                save_game()
            elif btn_load.collidepoint(mouse_pos):
                load_game()
            elif btn_exit.collidepoint(mouse_pos):
                running = False

        elif event.type == pygame.KEYDOWN:
            if restart_pending:
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
                    # Accept printable characters only
                    if event.unicode and event.unicode.isprintable():
                        input_text += event.unicode

    # Status timer countdown
    if status_timer > 0:
        status_timer -= 1
        if status_timer == 0:
            status_message = ""

    # --------------------------------------------------------------
    # Drawing
    # --------------------------------------------------------------
    screen.fill(BLACK)
    scenario = SCENARIOS[current_scenario]

    # Top menu bar background
    pygame.draw.rect(screen, (15, 15, 15), (0, 0, SCREEN_W, 48))
    pygame.draw.line(screen, DARK_GREEN, (0, 48), (SCREEN_W, 48), 1)

    # Buttons
    draw_button(btn_save, "SAVE", btn_save.collidepoint(mouse_pos))
    draw_button(btn_load, "LOAD", btn_load.collidepoint(mouse_pos))
    draw_button(btn_exit, "EXIT", btn_exit.collidepoint(mouse_pos))

    # Status message (right side of top bar)
    if status_message:
        status_surf = FONT_TINY.render(status_message, True, GREEN)
        screen.blit(status_surf, (SCREEN_W - status_surf.get_width() - 20, 14))

    # Media (right side)
    media = scenario.get("media")
    media_x = SCREEN_W - 380
    media_y = 70
    if media:
        media.draw(screen, (media_x, media_y))

    # Scenario text (left side)
    text_x = 30
    text_y = 70
    text_width = media_x - 60 if media else SCREEN_W - 60
    new_y = draw_text_wrapped(scenario["text"], FONT_MED, GREEN, text_x, text_y, text_width)

    # Input prompt or restart message
    if scenario["options"] and not restart_pending:
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 else " "
        prompt = "> " + input_text + cursor
        prompt_surf = FONT_LARGE.render(prompt, True, WHITE)
        screen.blit(prompt_surf, (text_x, new_y + 25))
    elif restart_pending:
        msg = FONT_LARGE.render("Press any key to restart", True, WHITE)
        screen.blit(msg, (text_x, new_y + 25))

    # Footer hint
    hint = FONT_TINY.render("Type the keyword or number then press ENTER  |  Click SAVE / LOAD / EXIT", True, LIGHT_GRAY)
    screen.blit(hint, (30, SCREEN_H - 28))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
