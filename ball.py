# Pong Tower - Ball
# =================

import pygame
import math
from settings import (
    BALL_START_RADIUS, BALL_MIN_RADIUS, BALL_START_SPEED,
    BALL_MAX_SPEED, BALL_SHRINK_PER_HIT, BALL_SPEED_INCREMENT,
    BALL_SPIN_FACTOR, BALL_COLOR, BALL_TRAIL_ALPHA,
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE
)

class Ball:
    def __init__(self):
        self.start_radius = BALL_START_RADIUS
        self.min_radius = BALL_MIN_RADIUS
        self.start_speed = BALL_START_SPEED
        self.max_speed = BALL_MAX_SPEED
        self.reset()

    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.radius = self.start_radius
        self.speed = self.start_speed
        self.vx = 0
        self.vy = 0
        self.trail = []
        self.serve_delay = 0
        self.angle = 0
        self.last_hit_by = None
        self.rally_count = 0

    def serve(self, direction: int = 1):
        """
        Launch ball.
        direction:  1 = up toward P1 (top paddle)
                   -1 = down toward P2 (bottom paddle)
        """
        import random, math
        self.serve_delay = 0
        # Vertical launch: angle mostly up/down, slight horizontal drift
        angle_deg = random.uniform(-30, 30)  # -30 to +30 degrees from vertical
        angle = math.radians(angle_deg)
        if direction > 0:
            self.angle = -math.pi / 2 + angle   # going up
        else:
            self.angle = math.pi / 2 + angle  # going down

        base_speed = self.start_speed - (self.start_radius - self.radius) * 0.05
        base_speed = max(base_speed, 4)
        self.speed = min(base_speed, self.max_speed)
        self._update_velocity()
        self.rally_count = 0

    def _update_velocity(self):
        import math
        self.vx = self.speed * math.cos(self.angle)
        self.vy = self.speed * math.sin(self.angle)

    def tick(self):
        """Move ball, update trail, manage serve delay."""
        if self.serve_delay > 0:
            self.serve_delay -= 1
            return

        self.x += self.vx
        self.y += self.vy

        # Wall bounce: LEFT / RIGHT walls
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.angle = math.pi - self.angle
            self._update_velocity()

        elif self.x + self.radius >= WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.radius
            self.angle = math.pi - self.angle
            self._update_velocity()

        # Trail
        self.trail.append((self.x, self.y, self.radius, BALL_TRAIL_ALPHA))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.trail = [(x, y, r, max(0, a - 8)) for x, y, r, a in self.trail if a > 0]

    def on_paddle_hit(self, paddle):
        """Ball hit top or bottom paddle — reflect toward opposite side."""
        import math
        self.rally_count += 1

        # Hit offset: where on the paddle did ball hit (-1=left, 0=center, 1=right)
        hit_offset = (self.x - paddle.rect.centerx) / max(1, paddle.rect.width / 2)
        hit_offset = max(-1, min(1, hit_offset))
        max_angle = 1.5  # ~85 degrees max deflection
        deflect = hit_offset * max_angle

        if paddle.side == "top":  # P1 hit -> ball should go DOWN
            self.angle = math.pi / 2 - deflect  # right-side hit -> deflects right
        else:  # P2 hit -> ball should go UP
            self.angle = -math.pi / 2 - deflect  # right-side hit -> deflects right (mirrors top)

        # Spin effect from boost timers
        if paddle.boost_timer > 0:
            self.angle += BALL_SPIN_FACTOR

        self.speed = min(self.speed + BALL_SPEED_INCREMENT, self.max_speed)
        self.radius = max(self.radius - BALL_SHRINK_PER_HIT, self.min_radius)
        self._update_velocity()

        # Burst ball outward so it doesn't stick inside paddle
        if paddle.side == "top":
            self.y = paddle.rect.bottom + self.radius + 1
        else:
            self.y = paddle.rect.top - self.radius - 1

    def is_out_top(self):
        return self.y + self.radius < 0

    def is_out_bottom(self):
        return self.y - self.radius > WINDOW_HEIGHT

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2)
        )

    def draw(self, surface):
        # Trail
        for x, y, r, alpha in self.trail:
            if alpha <= 0:
                continue
            trail_surf = pygame.Surface((int(r * 2), int(r * 2)), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*BALL_COLOR, int(alpha)), (int(r), int(r)), int(r))
            surface.blit(trail_surf, (x - r, y - r))

        # Main ball
        pygame.draw.circle(surface, BALL_COLOR, (int(self.x), int(self.y)), int(self.radius))

        # Inner glare
        inner_r = max(2, int(self.radius * 0.35))
        pygame.draw.circle(surface, WHITE, (int(self.x - self.radius * 0.25), int(self.y - self.radius * 0.25)), inner_r)
