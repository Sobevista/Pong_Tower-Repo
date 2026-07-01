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

KEY_MAP = {
    pygame.K_1: 0,
    pygame.K_2: 1,
    pygame.K_a: 0,
    pygame.K_s: 0,
    pygame.K_k: 1,
    pygame.K_l: 1,
    pygame.K_UP: -1,
    pygame.K_DOWN: 1,
    pygame.K_w: -1,
    pygame.K_s: 1,
}


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
                if event.key in KEY_MAP:
                    idx = KEY_MAP[event.key]
                    if idx == -1:
                        self.selected = (self.selected - 1) % len(OPTIONS)
                    elif idx == 1:
                        self.selected = (self.selected + 1) % len(OPTIONS)
                    else:
                        return OPTIONS[idx][0]
                if event.key == pygame.K_RETURN:
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
