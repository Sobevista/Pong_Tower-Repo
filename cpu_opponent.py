# Pong Tower - CPU Opponent
# ==========================

import random
import math
from settings import PADDLE_SPEED, WINDOW_WIDTH

class CPU:
    def __init__(self, difficulty: float = 0.5):
        """
        difficulty: 0.0 to 1.0
          0.0 = barely moves, 1.0 = perfect tracking
        """
        self.base_difficulty = max(0.0, min(1.0, difficulty))
        # NOTE: difficulty currently only narrows error_margin (jitter).
        # A reaction-lag mechanic (delay before CPU starts tracking a new
        # incoming ball) would be a good next enhancement for making
        # higher floors feel meaningfully harder, not just more accurate.
        self.error_margin = (1.0 - self.base_difficulty) * 60      # px of "noise" added to target
        self.current_error_x = 0
        self.current_error_timer = 0

    def get_move(self, paddle_rect, ball) -> str:
        """
        Returns a move string: 'left', 'right', or None.
        paddle_rect: the CPU's paddle
        ball: the ball object
        """
        # Only react when ball is coming toward the bottom paddle
        # (vy > 0 = moving down). This must be a SIGN check, not a
        # magnitude threshold: the old `vy < 0.5` went permanently blind
        # to max-deflection edge hits, where a legally descending ball
        # has vy ~= 0.45 — the CPU idled while the ball crawled past it.
        if ball.vy <= 0:  # ball moving up or perfectly horizontal — stay idle
            return None

        # Jitter target slightly so CPU isn't robotic
        if self.current_error_timer <= 0:
            self.current_error_x = random.uniform(-self.error_margin, self.error_margin)
            self.current_error_timer = random.randint(15, 45)

        self.current_error_timer -= 1
        target_x = ball.x + self.current_error_x

        # Clamp target to full screen so CPU can reach any ball position
        # paddle_rect.width alone caps the target at ~100px → CPU always goes left
        target_half = paddle_rect.width // 2
        target_x = max(target_half, min(target_x, WINDOW_WIDTH - target_half))

        threshold = paddle_rect.width * 0.3  # dead zone
        if paddle_rect.centerx < target_x - threshold:
            return "right"
        elif paddle_rect.centerx > target_x + threshold:
            return "left"
        return None

    def update_difficulty(self, difficulty: float):
        self.base_difficulty = max(0.0, min(1.0, difficulty))
        self.error_margin = (1.0 - self.base_difficulty) * 60
