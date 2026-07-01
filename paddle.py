# Pong Tower - Paddle
# ====================

import pygame
from settings import (
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED,
    PADDLE_MARGIN, WINDOW_WIDTH, WINDOW_HEIGHT, PADDLE_CORNER_RADIUS,
    PADDLE_COLOR_P1, PADDLE_COLOR_P2, GREEN
)

class Paddle:
    def __init__(self, player_id: int, side: str):
        """
        side: 'top' or 'bottom'
          top    — P1, moves LEFT/RIGHT along top edge
          bottom — P2, moves LEFT/RIGHT along bottom edge
        """
        self.player_id = player_id
        self.side = side
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.base_speed = PADDLE_SPEED
        self.color = PADDLE_COLOR_P1 if side == "top" else PADDLE_COLOR_P2
        self.score = 0

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self._position_on_side()

        self.upgrade_level = 0
        self.boost_timer = 0
        self.wide_timer = 0

    def _position_on_side(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        if self.side == "top":
            self.rect.y = PADDLE_MARGIN - self.height // 2
        else:
            self.rect.y = WINDOW_HEIGHT - PADDLE_MARGIN - self.height // 2
        self.rect.x = max(0, min(self.rect.x, WINDOW_WIDTH - self.width))

    def reset(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        self.boost_timer = 0
        self.wide_timer = 0

    def get_current_speed(self):
        boost = 1.6 if self.boost_timer > 0 else 1.0
        return self.base_speed * boost

    def get_current_width(self):
        if self.wide_timer > 0:
            return int(self.width * 1.6)
        return self.width

    def tick(self):
        if self.boost_timer > 0:
            self.boost_timer -= 1
        if self.wide_timer > 0:
            self.wide_timer -= 1

    def move_left(self):
        self.rect.x = max(self.rect.x - self.get_current_speed(), 0)

    def move_right(self):
        self.rect.right = min(self.rect.right + self.get_current_speed(), WINDOW_WIDTH)

    def apply_boost(self, frames=180):
        self.boost_timer = max(self.boost_timer, frames)

    def apply_wide(self, frames=300):
        self.wide_timer = max(self.wide_timer, frames)

    def draw(self, surface):
        color = list(self.color)
        if self.boost_timer > 0:
            color = GREEN
        pygame.draw.rect(
            surface,
            color,
            self.rect,
            border_radius=PADDLE_CORNER_RADIUS
        )
