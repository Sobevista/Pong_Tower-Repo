# Pong Tower - Test Suite
import unittest
import pygame
import math
from unittest.mock import patch, MagicMock
from game import PongGame, STATE_PLAYING, STATE_PAUSED
from paddle import Paddle
from ball import Ball
from settings import WINDOW_HEIGHT
from start_screen import StartScreen

class TestPongGame(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = PongGame(mode="multiplayer")
        
    def tearDown(self):
        pygame.quit()
        
    def test_paddle_no_move_during_pause(self):
        self.game.state = STATE_PAUSED
        initial_x = self.game.p1.rect.x
        
        fake_keys = MagicMock()
        fake_keys.__getitem__ = lambda self, key: True if key == pygame.K_a else False
        with patch('pygame.key.get_pressed', return_value=fake_keys):
            self.game.handle_input()
        
        self.assertEqual(self.game.p1.rect.x, initial_x, "Paddle moved while paused!")

    def test_bottom_paddle_deflection(self):
        self.game.ball.y = self.game.p2.rect.top - 5
        self.game.ball.vy = 5
        self.game.ball.on_paddle_hit(self.game.p2)
        self.assertLess(self.game.ball.vy, 0, f"Ball didn't bounce up! vy={self.game.ball.vy}")

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

    def test_serve_direction_toward_top(self):
        """Ball should go UP when direction=1 (toward top/P1)."""
        ball = Ball()
        ball.serve(direction=1)
        self.assertLess(ball.vy, 0, f"serve(direction=1) should go up, got vy={ball.vy}")

    def test_serve_direction_toward_bottom(self):
        """Ball should go DOWN when direction=-1 (toward bottom/P2)."""
        ball = Ball()
        ball.serve(direction=-1)
        self.assertGreater(ball.vy, 0, f"serve(direction=-1) should go down, got vy={ball.vy}")

class TestStartScreen(unittest.TestCase):
    """Regression tests for the start screen. The original bug report:
    'the title screen does not allow me to interact' -- total unresponsiveness,
    not a partial key-mapping issue."""

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))  # headless-safe minimal surface

    def tearDown(self):
        pygame.event.clear()
        pygame.quit()

    def test_menu_responds_to_single_event_get_call(self):
        """Root cause of 'menu is completely unresponsive': game.py's __main__
        block used to call pygame.event.get() once to check for QUIT, then
        called menu.handle_input() -- which calls pygame.event.get() again.
        The first call drains the queue, so the second one always sees an
        empty queue. This test simulates the CORRECT pattern (single
        event.get() call, inside handle_input only) and confirms a keypress
        is actually seen. If someone reintroduces an outer event.get() call
        around the menu loop, this test won't catch that directly -- but it
        documents the exact failure mode so it doesn't get reintroduced
        silently. See HANDOFF.md / SKILLS.md pitfall notes.
        """
        menu = StartScreen()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
        result = menu.handle_input()
        self.assertEqual(result, "tower", "Menu did not respond to ENTER at all")

    def test_pressing_1_selects_tower_directly(self):
        menu = StartScreen()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_1}))
        self.assertEqual(menu.handle_input(), "tower")

    def test_pressing_2_selects_multiplayer_directly(self):
        """Regression test: hint text says 'ENTER or 1/2 = Select', but the
        old KEY_MAP overloaded the same int both as a nav direction and an
        option index, so pressing 2 just moved the cursor down instead of
        selecting Multiplayer."""
        menu = StartScreen()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_2}))
        self.assertEqual(menu.handle_input(), "multiplayer")

    def test_navigation_then_enter_selects_highlighted_option(self):
        menu = StartScreen()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
        self.assertIsNone(menu.handle_input(), "DOWN alone should only move the cursor")
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
        self.assertEqual(menu.handle_input(), "multiplayer")


if __name__ == "__main__":
    unittest.main()
