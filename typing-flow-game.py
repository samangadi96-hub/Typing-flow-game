import pygame
import random
import sys

pygame.init()

# ================= WINDOW =================
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Flow ⚡")
clock = pygame.time.Clock()

# ================= FONTS =================
title_font = pygame.font.SysFont("arial", 60, bold=True)
subtitle_font = pygame.font.SysFont("arial", 28)
word_font = pygame.font.SysFont("arial", 80, bold=True)
input_font = pygame.font.SysFont("arial", 46)
info_font = pygame.font.SysFont("arial", 28)

# ================= COLORS =================
BG = (12, 14, 20)
PANEL = (22, 24, 34)
TEXT_MAIN = (240, 240, 250)

CYAN = (120, 200, 255)
VIOLET = (190, 160, 255)
PINK = (255, 140, 180)
SAGE = (140, 220, 180)
AMBER = (255, 210, 140)
GRAY = (160, 165, 175)
RED = (255, 100, 120)

# ================= PARTICLES =================
class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.r = random.randint(1, 3)
        self.s = random.uniform(0.3, 1)
        self.c = random.choice([CYAN, VIOLET, SAGE])

    def update(self):
        self.y += self.s
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        pygame.draw.circle(screen, self.c, (int(self.x), int(self.y)), self.r)

particles = [Particle() for _ in range(120)]

# ================= WORD DATA =================
WORD_SETS = {
    "EASY": ["cat","dog","sun","pen","cup","hat","box","car","toy","ball"],
    "MEDIUM": ["python","typing","keyboard","random","screen",
               "object","method","function","variable","string"],
    "HARD": ["optimization","development","architecture","abstraction",
             "polymorphism","inheritance","encapsulation"],
    "VERY HARD": ["cryptographic","electromagnetism","microarchitecture",
                  "bioinformatics","electroencephalogram"]
}

WORDS_PER_LEVEL = 10
TOTAL_LIVES = 5

# ================= GAME STATE =================
state = "LEVEL_SELECT"
level = "EASY"

words_pool = []
current_word = ""
typed_text = ""

score = 0
lives = TOTAL_LIVES
words_done = 0
start_time = 0
total_time = 0
total_keys = 0
mistakes = 0

# feedback + pause
feedback_text = ""
pause_until = 0
pending_next = False

# ================= FUNCTIONS =================
def draw_center(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)

def prepare_words():
    global words_pool
    words_pool = WORD_SETS[level].copy()
    random.shuffle(words_pool)

def next_word():
    global current_word, typed_text, start_time, state
    if not words_pool:
        state = "GAME_OVER"
        return
    current_word = words_pool.pop()
    typed_text = ""
    start_time = pygame.time.get_ticks()

def reset_game():
    global score, lives, words_done, total_time, total_keys, mistakes
    score = 0
    lives = TOTAL_LIVES
    words_done = 0
    total_time = 0
    total_keys = 0
    mistakes = 0
    prepare_words()
    next_word()

# ================= MAIN LOOP =================
running = True
while running:
    screen.fill(BG)

    for p in particles:
        p.update()
        p.draw()

    now = pygame.time.get_ticks()

    # delayed next word after mistake
    if pending_next and now >= pause_until:
        pending_next = False
        feedback_text = ""
        next_word()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # LEVEL SELECT
        if state == "LEVEL_SELECT" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                level = "EASY"; reset_game(); state = "PLAYING"
            elif event.key == pygame.K_2:
                level = "MEDIUM"; reset_game(); state = "PLAYING"
            elif event.key == pygame.K_3:
                level = "HARD"; reset_game(); state = "PLAYING"
            elif event.key == pygame.K_4:
                level = "VERY HARD"; reset_game(); state = "PLAYING"

        # PLAYING
        elif state == "PLAYING" and event.type == pygame.KEYDOWN:
            if now < pause_until:
                continue  # ignore input during pause

            if event.key == pygame.K_BACKSPACE:
                typed_text = typed_text[:-1]

            elif event.unicode.isprintable():
                total_keys += 1
                typed_text += event.unicode

                if not current_word.startswith(typed_text):
                    mistakes += 1
                    lives -= 1
                    words_done += 1

                    feedback_text = "❌ Wrong letter"
                    pause_until = now + 2000
                    pending_next = True

            if typed_text == current_word:
                score += 1
                words_done += 1
                total_time += (now - start_time) / 1000
                next_word()

        elif state == "GAME_OVER" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                state = "LEVEL_SELECT"

    # ================= UI =================
    if state == "PLAYING":
        pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 90))
        screen.blit(info_font.render(f"Level: {level}", True, CYAN), (30, 35))
        screen.blit(info_font.render(f"Score: {score}", True, SAGE), (380, 35))
        screen.blit(info_font.render(f"Lives: {lives}", True, PINK), (680, 35))
        screen.blit(info_font.render(f"Word: {words_done}/{WORDS_PER_LEVEL}", True, GRAY), (960, 35))

        draw_center(current_word, word_font, TEXT_MAIN, HEIGHT // 2 - 60)
        draw_center(typed_text, input_font, VIOLET, HEIGHT // 2 + 40)

        if feedback_text:
            draw_center(feedback_text, subtitle_font, RED, HEIGHT // 2 + 120)

        if lives <= 0 or words_done >= WORDS_PER_LEVEL:
            state = "GAME_OVER"

    elif state == "LEVEL_SELECT":
        draw_center("Typing Flow", title_font, TEXT_MAIN, 200)
        draw_center("Enter the flow. Make mistakes. Get faster.", subtitle_font, GRAY, 260)

        draw_center("1  EASY", info_font, CYAN, 340)
        draw_center("2  MEDIUM", info_font, VIOLET, 380)
        draw_center("3  HARD", info_font, AMBER, 420)
        draw_center("4  VERY HARD", info_font, PINK, 460)

    elif state == "GAME_OVER":
        accuracy = 100 if total_keys == 0 else int(((total_keys - mistakes) / total_keys) * 100)
        wpm = int((words_done / total_time) * 60) if total_time > 0 else 0

        draw_center("GAME OVER", title_font, PINK, 200)
        draw_center(f"WPM: {wpm}", info_font, AMBER, 300)
        draw_center(f"Accuracy: {accuracy}%", info_font, CYAN, 340)
        draw_center("Press R to Restart", info_font, GRAY, 420)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()