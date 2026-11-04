import pygame
import sys
import textwrap
import os
import gif_pygame

# ------------------------------------------------------------------
# 1. INITIALISE PYGAME & MIXER SUBSYSTEMS
# ------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 1050, 750
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("The Matrix – Extended Text Adventure")
clock = pygame.time.Clock()

# Typography Hierarchy
FONT_LARGE = pygame.font.Font(None, 38)
FONT_MED = pygame.font.Font(None, 28)
FONT_SMALL = pygame.font.Font(None, 20)

# Colour Palette Constants
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ------------------------------------------------------------------
# 2. AUDIO MANAGEMENT (MP3 Background Music)
# ------------------------------------------------------------------
def init_background_audio(filepath="media/matrix_theme.mp3"):
    """
    Initializes and streams background audio loops with exception safety.
    """
    if os.path.exists(filepath):
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1) # -1 ensures infinite looping
        except pygame.error as e:
            print(f"[Audio Warning] Failed to decode MP3 stream: {e}")
    else:
        print(f"[Audio Notice] Target audio file '{filepath}' not found. Running in mute mode.")

init_background_audio()

# ------------------------------------------------------------------
# 3. MEDIA HANDLING (Safe Asset Ingestion)
# ------------------------------------------------------------------
class Media:
    """Load and display either a still image or an animated GIF with error safety."""
    def __init__(self, path, size=(350, 250), is_gif=False):
        self.path = path
        self.size = size
        self.is_gif = is_gif
        self.asset = None
        
        if os.path.exists(path):
            try:
                if is_gif:
                    self.asset = gif_pygame.load(path)
                    self.asset = gif_pygame.transform.scale(self.asset, size)
                else:
                    self.asset = pygame.image.load(path).convert_alpha()
                    self.asset = pygame.transform.scale(self.asset, size)
            except Exception as e:
                print(f"[Media Warning] Could not load asset {path}: {e}")
                self.asset = None
        else:
            print(f"[Media Notice] Asset path missing: {path}")
            self.asset = None

    def draw(self, surface, pos):
        if self.asset:
            if self.is_gif:
                self.asset.render(surface, pos)
            else:
                surface.blit(self.asset, pos)

# ------------------------------------------------------------------
# 4. EXPANDED SCENARIO TOPOLOGY (Sourced from the_matrix.pdf)
# ------------------------------------------------------------------
SCENARIOS = {
    "start": {
        "text": (
            "You are Neo, a hacker living a double life. A message flashes on your screen:\n"
            "‘Wake up, Neo. The Matrix has you. Follow the white rabbit.’[cite: 12]\n\n"
            "Someone knocks on your door. Choi asks you to go out to the club[cite: 12].\n"
            "Choices:\n"
            "1. stay - Stay home and work on your computer.\n"
            "2. club - Go out to the club with Choi and look for the white rabbit."
        ),
        "options": {"stay": "stay_caught", "club": "club_meet"},
        "media": Media("media/neo.png", (350, 250), is_gif=False)
    },
    "stay_caught": {
        "text": (
            "You stay home. The next morning at Meta CorTechs, Rhineheart warns you about your attitude[cite: 16]. "
            "Shortly after, Agents arrive at your cubicle[cite: 17]. You are captured and brought in for interrogation[cite: 20].\n\n"
            "GAME OVER – Press 'r' or any key to restart."
        ),
        "options": {},
        "media": Media("media/digital_rain.gif", (400, 300), is_gif=True)
    },
    "club_meet": {
        "text": (
            "At the club, you notice a woman with a small white rabbit tattoo on her jacket: Trinity[cite: 13]. "
            "She approaches you and whispers:\n"
            "‘The answer is out there, Neo. It's looking for you and it will find you, if you want it to.’[cite: 16]\n\n"
            "The next day at work, a FedEx package arrives containing a cell phone. Morpheus calls you, guiding you to escape the Agents[cite: 17, 18].\n\n"
            "Choices:\n"
            "1. scaffold - Try to escape across the dangerous building scaffolding[cite: 18].\n"
            "2. surrender - Give up and surrender to Agent Smith."
        ),
        "options": {"scaffold": "interrogation", "surrender": "stay_caught"},
        "media": Media("media/digital_rain.gif", (400, 300), is_gif=True)
    },
    "interrogation": {
        "text": (
            "You attempt the escape, but slip and get captured by the Agents. "
            "In the interrogation room, Agent Smith slides a file across the table and says:\n"
            "‘We are willing to wipe the slate clean... all we are asking in return is your cooperation in bringing a known terrorist to justice... Morpheus.’[cite: 20, 24]\n\n"
            "Neo: ‘How about I just give you the finger... And you give me my phone call!’[cite: 24]\n"
            "Smith seals your mouth shut and implants a horrific bug into your stomach[cite: 25]. "
            "You wake up in bed—was it a dream? The phone rings[cite: 25].\n\n"
            "Choices:\n"
            "1. bridge - Answer the phone and agree to meet Morpheus at the Adams Street bridge[cite: 26].\n"
            "2. ignore - Ignore the call and stay in bed."
        ),
        "options": {"bridge": "morpheus_meet", "ignore": "stay_caught"},
        "media": Media("media/red_pill.gif", (400, 300), is_gif=True)
    },
    "morpheus_meet": {
        "text": (
            "Trinity and her crew pick you up, extract the bug from your stomach[cite: 28], and bring you to Room 1313 to meet Morpheus[cite: 27].\n"
            "Morpheus: ‘You have the look of a man who accepts what he sees because he is expecting to wake up... "
            "Unfortunately, no one can be told what the Matrix is. You have to see it for yourself.’[cite: 28, 29]\n\n"
            "He opens his hands: ‘This is your last chance. After this, there is no going back.’[cite: 29]\n"
            "Choices:\n"
            "1. red - Take the red pill and discover the truth of the desert of the real[cite: 29, 42].\n"
            "2. blue - Take the blue pill and wake up in your bed believing whatever you want[cite: 29]."
        ),
        "options": {"red": "real_world_awakening", "blue": "stay_caught"},
        "media": Media("media/red_pill.gif", (400, 300), is_gif=True)
    },
    "real_world_awakening": {
        "text": (
            "You wake up naked and slimy inside a liquid-filled pod, a cable plugged directly into the back of your skull[cite: 36]. "
            "You are rescued by the Nebuchadnezzar hovercraft[cite: 37]. Morpheus welcomes you to the real world[cite: 37]. "
            "After recovering, you undergo intense combat loading programs (Jujitsu, Kung Fu)[cite: 49] and jump training.\n\n"
            "Next, Morpheus takes you to visit the Oracle to find your path[cite: 67].\n"
            "Choices:\n"
            "1. oracle - Meet the Oracle and the Spoon Boy in her kitchen[cite: 70, 71].\n"
            "2. skip - Skip the Oracle visit and stay on the ship."
        ),
        "options": {"oracle": "oracle_visit", "skip": "building_trap"},
        "media": Media("media/morpheus.jpg", (350, 250), is_gif=False)
    },
    "oracle_visit": {
        "text": (
            "Inside the Oracle's apartment, a Spoon Boy hands you a spoon and tells you: "
            "‘Do not try to bend the spoon. That is impossible. Instead, only try to realize the truth... There is no spoon.’[cite: 74]\n\n"
            "The Oracle bakes cookies and tells you your fortune[cite: 75, 76]:\n"
            "‘Sorry, kid. You got the gift, but looks like you're waiting for something... Your next life, maybe.’[cite: 77]\n"
            "She warns you that Morpheus will sacrifice his life to save yours, forcing you to choose between your life and his[cite: 78].\n\n"
            "Choices:\n"
            "1. betrayal - Cypher betrays the crew to the Agents at the hotel trap[cite: 93].\n"
            "2. fight - Stand your ground against Agent Smith in the building walls[cite: 87]."
        ),
        "options": {"betrayal": "building_trap", "fight": "building_trap"},
        "media": Media("media/morpheus.jpg", (350, 250), is_gif=False)
    },
    "building_trap": {
        "text": (
            "A trap springs! Cypher's betrayal leads the Agents straight to you[cite: 93]. Mouse is killed[cite: 98], and Morpheus allows himself to be captured by Agent Smith to protect Neo[cite: 87].\n\n"
            "Tank tells the team that Morpheus will soon break under interrogation and give up the mainframe access codes to Zion[cite: 100].\n"
            "Neo refuses to abandon Morpheus: ‘I'm going in... I believe I can bring him back.’[cite: 102, 103]\n\n"
            "Choices:\n"
            "1. rescue - Load up with 'Lots of guns' and launch a suicidal rescue mission on the government building[cite: 105].\n"
            "2. abandon - Leave Morpheus behind and accept Zion's destruction."
        ),
        "options": {"rescue": "lobby_gunfight", "abandon": "stay_caught"},
        "media": Media("media/neo.png", (350, 250), is_gif=False)
    },
    "lobby_gunfight": {
        "text": (
            "You and Trinity burst through the revolving doors of the government building[cite: 107]. "
            "Security guard: ‘Would you please remove any metallic items you are carrying...’[cite: 108]\n"
            "You open your trench coat, revealing an overwhelming arsenal, and execute a breathtaking lobby shootout[cite: 108]. "
            "You scale the elevator shaft, blow the cables, and make it to the rooftop where you face Agent Jones in slow-motion Bullet-Time[cite: 109, 111]!\n\n"
            "Trinity saves the day: ‘Dodge this!’[cite: 112] You pilot a B-212 military helicopter straight into the executive office to rescue Morpheus[cite: 112, 113].\n\n"
            "Choices:\n"
            "1. subway - Escape through the subway station where Agent Smith waits for you[cite: 116, 118].\n"
            "2. surrender_agent - Surrender to Agent Smith."
        ),
        "options": {"subway": "subway_showdown", "surrender_agent": "stay_caught"},
        "media": Media("media/neo.png", (350, 250), is_gif=False)
    },
    "subway_showdown": {
        "text": (
            "At the subway station, Agent Smith confronts you[cite: 118].\n"
            "Smith: ‘I'm going to enjoy watching you die, Mr. Anderson.’[cite: 120]\n"
            "After a brutal clash on the tracks, an oncoming train strikes Smith[cite: 121]. You flee through the city alleys toward room 303[cite: 124, 125]. "
            "Tragically, Agent Smith ambushes you at the door and shoots you dead[cite: 128].\n\n"
            "Back on the hovercraft, Trinity refuses to accept your death:\n"
            "‘You can't be dead, Neo, you can't be because I love you... I love you!’[cite: 129] She kisses you[cite: 130].\n\n"
            "Choices:\n"
            "1. revive - Your eyes snap open. You are truly becoming The One[cite: 130].\n"
            "2. stay_dead - Stay dead and let the machines win."
        ),
        "options": {"revive": "hero_victory", "stay_dead": "stay_caught"},
        "media": Media("media/neo.png", (350, 250), is_gif=False)
    },
    "hero_victory": {
        "text": (
            "You stand up. The bullets fired by the Agents freeze in mid-air and drop harmlessly to the floor[cite: 130]. "
            "You see through the code of the Matrix[cite: 130], thrust your hand into Agent Smith, and destroy him from within[cite: 131]!\n\n"
            "CONGRATULATIONS – You have liberated your mind, saved Morpheus, and become the hero of the Matrix[cite: 132]!\n"
            "Press any key to restart."
        ),
        "options": {},
        "media": Media("media/neo.png", (350, 250), is_gif=False)
    }
}

# ------------------------------------------------------------------
# 5. GAME STATE & HELPERS
# ------------------------------------------------------------------
current_scenario = "start"
input_text = ""
restart_pending = False

def draw_text_wrapped(text, font, colour, x, y, max_width):
    """Draw multi-line text with word wrapping, returning the new y position."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] < max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
    for line in lines:
        surface = font.render(line, True, colour)
        screen.blit(surface, (x, y))
        y += font.get_linesize()
    return y

def reset_game():
    global current_scenario, input_text, restart_pending
    current_scenario = "start"
    input_text = ""
    restart_pending = False

# ------------------------------------------------------------------
# 6. MAIN LOOP
# ------------------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
                    else:
                        input_text = ""
                        continue
                input_text = ""
                if not SCENARIOS[current_scenario]["options"]:
                    restart_pending = True
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if not restart_pending and SCENARIOS[current_scenario]["options"]:
                    input_text += event.unicode

    # --------------------------------------------------------------
    # DRAW PIPELINE
    # --------------------------------------------------------------
    screen.fill(BLACK)
    scenario = SCENARIOS[current_scenario]

    # 1) Media (Right Side)
    if scenario.get("media"):
        media = scenario["media"]
        media_x = SCREEN_W - media.size[0] - 30
        media_y = 30
        media.draw(screen, (media_x, media_y))

    # 2) Scenario Text (Left Side)
    text_x = 30
    text_y = 30
    text_width = SCREEN_W - (scenario["media"].size[0] + 60) if scenario.get("media") else SCREEN_W - 60
    new_y = draw_text_wrapped(scenario["text"], FONT_MED, GREEN, text_x, text_y, text_width)

    # 3) Input Box / Prompt State
    if scenario["options"] and not restart_pending:
        prompt = "> " + input_text + ("_" if pygame.time.get_ticks() // 500 % 2 else "")
        prompt_surface = FONT_LARGE.render(prompt, True, WHITE)
        input_y = new_y + 20
        screen.blit(prompt_surface, (text_x, input_y))
    elif restart_pending:
        restart_msg = FONT_LARGE.render("Press any key to restart", True, WHITE)
        screen.blit(restart_msg, (text_x, new_y + 20))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()