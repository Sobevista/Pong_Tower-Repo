# Pong Tower - INVARIANT TEST SUITE (human-owned, agent-read-only)
# ================================================================
# These encode laws of the system that must hold across ANY refactor.
# If a change breaks one of these, the change is wrong. Do not weaken
# these tests to make a build pass. See tests/invariants/README.md.

import os
import math
import unittest

# Run headless so this suite has no display/audio dependency.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from paddle import Paddle
from ball import Ball
from settings import WINDOW_WIDTH, BALL_MAX_SPEED


class PaddleInvariants(unittest.TestCase):
    def test_paddle_never_exits_left_edge(self):
        p = Paddle(player_id=1, side="top")
        for _ in range(1000):
            p.move_left()
        self.assertGreaterEqual(p.rect.x, 0, "Paddle escaped the left wall")

    def test_paddle_never_exits_right_edge(self):
        p = Paddle(player_id=2, side="bottom")
        for _ in range(1000):
            p.move_right()
        self.assertLessEqual(
            p.rect.right, WINDOW_WIDTH, "Paddle escaped the right wall"
        )

    def test_reset_recenters_paddle(self):
        p = Paddle(player_id=1, side="top")
        for _ in range(50):
            p.move_right()
        p.reset()
        self.assertEqual(
            p.rect.centerx, WINDOW_WIDTH // 2, "reset() did not re-center paddle"
        )


class BallInvariants(unittest.TestCase):
    def test_serve_speed_within_bounds(self):
        b = Ball()
        for direction in (1, -1):
            for _ in range(200):
                b.serve(direction)
                self.assertGreaterEqual(b.speed, 4, "Serve speed dropped below floor")
                self.assertLessEqual(
                    b.speed, BALL_MAX_SPEED, "Serve speed exceeded BALL_MAX_SPEED"
                )

    def test_serve_direction_is_correct(self):
        b = Ball()
        # direction 1 = up toward P1 (top) => negative vy (screen y grows downward)
        for _ in range(200):
            b.serve(1)
            self.assertLess(b.vy, 0, "Serve toward P1 was not launched upward")
        # direction -1 = down toward P2 (bottom) => positive vy
        for _ in range(200):
            b.serve(-1)
            self.assertGreater(b.vy, 0, "Serve toward P2 was not launched downward")

    def test_velocity_magnitude_matches_speed(self):
        b = Ball()
        for direction in (1, -1):
            b.serve(direction)
            mag = math.hypot(b.vx, b.vy)
            self.assertAlmostEqual(
                mag, b.speed, places=4,
                msg="Velocity magnitude diverged from scalar speed",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
