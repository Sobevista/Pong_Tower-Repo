# Pong Tower - Start Screen
# ==========================

import pygame
import sys
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR, CENTER_LINE_COLOR,
    WHITE, GOLD, GREEN
)

OPTIONS = [
    ("tower",        "PONG TOWER",       "Climb the tower. Affixes, floors, unlocks."),
    ("multiplayer",  "MULTIPLIER",        "Endless casual play. No rules, no mercy."),
]

# Matches the on-screen hint text exactly: "W/S or UP/DOWN = Navigate
# ENTER or 1/2 = Select". Previously these were combined into one
# overloaded dict where the value doubled as both a navigation direction
# and an option index -- which meant pressing "2" moved the cursor down
# instead of selecting MULTIPLIER directly, contradicting the hint text.
NAV_UP_KEYS = {pygame.K_UP, pygame.K_w}
NAV_DOWN_KEYS = {pygame.K_DOWN, pygame.K_s}
DIRECT_SELECT_KEYS = {pygame.K_1: 0, pygame.K_2: 1}


class StartScreen:
    def __init__(self):
        self.title_font = pygame.font.SysFont("consolas", 72, bold=True)
        self.option_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.desc_font = pygame.font.SysFont("consolas", 20)
        self.hint_font = pygame.font.SysFont("consolas", 18)
        self.selected = 0
        self.pulse = 0

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit(0)
                if event.key in NAV_UP_KEYS:
                    self.selected = (self.selected - 1) % len(OPTIONS)
                elif event.key in NAV_DOWN_KEYS:
                    self.selected = (self.selected + 1) % len(OPTIONS)
                elif event.key in DIRECT_SELECT_KEYS:
                    return OPTIONS[DIRECT_SELECT_KEYS[event.key]][0]
                elif event.key == pygame.K_RETURN:
                    return OPTIONS[self.selected][0]
        return None

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        self.pulse += 0.03

        # Title
        title = self.title_font.render("PONG TOWER", True, GOLD)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        sub = self.hint_font.render("A retro game system by Daniel", True, WHITE)
        screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 160))

        pygame.draw.line(screen, CENTER_LINE_COLOR, (100, 200), (WINDOW_WIDTH - 100, 200), 2)

        # Smooth selection pulse — alternate every 40 frames (~0.67s)
        selected_arrow = ">" if (self.pulse % 1.0) < 0.65 else " "

        for i, (mode_key, name, desc) in enumerate(OPTIONS):
            y = 250 + i * 110
            is_selected = i == self.selected

            arrow = selected_arrow if is_selected else " "
            color = GOLD if is_selected else WHITE

            name_surf = self.option_font.render(f"  {arrow} {name}", True, color)
            screen.blit(name_surf, (WINDOW_WIDTH // 2 - name_surf.get_width() // 2, y))

            desc_surf = self.desc_font.render(desc, True, color)
            screen.blit(desc_surf, (WINDOW_WIDTH // 2 - desc_surf.get_width() // 2, y + 40))

        # Bottom hints
        hints = [
            "W/S or UP/DOWN = Navigate    ENTER or 1/2 = Select    ESC = Quit",
        ]
        for i, h in enumerate(hints):
            hs = self.hint_font.render(h, True, WHITE)
            screen.blit(hs, (WINDOW_WIDTH // 2 - hs.get_width() // 2, WINDOW_HEIGHT - 40))

        pygame.display.flip()
