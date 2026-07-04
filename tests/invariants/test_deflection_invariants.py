# Pong Tower - Deflection Invariants
#
# HUMAN-OWNED. Do not modify these tests. If a change makes one of these
# fail, the change is wrong, not the test. See README.md in this directory.
#
# Copied from test_pong.py (TestPongGame) -- not moved. test_pong.py keeps
# its own copies; these are the CI-enforced source of truth.
import unittest
import pygame

from game import PongGame


class TestDeflectionInvariants(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = PongGame(mode="multiplayer")

    def tearDown(self):
        pygame.quit()

    def test_bottom_paddle_right_edge_deflects_right(self):
        """Regression test: a prior fix flipped vy sign but left vx inverted —
        right-edge hits were deflecting the ball LEFT instead of RIGHT."""
        self.game.ball.x = self.game.p2.rect.centerx + (self.game.p2.rect.width * 0.4)
        self.game.ball.y = self.game.p2.rect.top - 5
        self.game.ball.vy = 5
        self.game.ball.on_paddle_hit(self.game.p2)
        self.assertGreater(self.game.ball.vx, 0,
            f"Right-edge hit on bottom paddle should deflect ball RIGHT, got vx={self.game.ball.vx}")

    def test_bottom_paddle_left_edge_deflects_left(self):
        self.game.ball.x = self.game.p2.rect.centerx - (self.game.p2.rect.width * 0.4)
        self.game.ball.y = self.game.p2.rect.top - 5
        self.game.ball.vy = 5
        self.game.ball.on_paddle_hit(self.game.p2)
        self.assertLess(self.game.ball.vx, 0,
            f"Left-edge hit on bottom paddle should deflect ball LEFT, got vx={self.game.ball.vx}")

    def test_top_bottom_deflection_symmetry(self):
        """Both paddles should deflect a same-side hit in the same horizontal
        direction — only the vertical direction (up vs down) should differ."""
        self.game.ball.x = self.game.p1.rect.centerx + (self.game.p1.rect.width * 0.4)
        self.game.ball.y = self.game.p1.rect.bottom + 5
        self.game.ball.vy = -5
        self.game.ball.on_paddle_hit(self.game.p1)
        top_vx_sign = self.game.ball.vx > 0

        self.game.ball.x = self.game.p2.rect.centerx + (self.game.p2.rect.width * 0.4)
        self.game.ball.y = self.game.p2.rect.top - 5
        self.game.ball.vy = 5
        self.game.ball.on_paddle_hit(self.game.p2)
        bottom_vx_sign = self.game.ball.vx > 0

        self.assertEqual(top_vx_sign, bottom_vx_sign,
            "Top and bottom paddles deflect the same-side hit in opposite horizontal directions")


if __name__ == "__main__":
    unittest.main()
