# Pong Tower - Test Suite
import unittest
import os
import tempfile
import pygame
import math
from unittest.mock import patch, MagicMock
from game import (
    PongGame, STATE_PLAYING, STATE_PAUSED, STATE_SERVE, STATE_WIN,
    STATE_CONFIRM_QUIT, STATE_TOWER_INTRO, STATE_GAME_OVER
)
from paddle import Paddle
from ball import Ball
from cpu_opponent import CPU
from achievements import AchievementManager
from settings import WINDOW_HEIGHT, WINDOW_WIDTH
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

class TestAdversarialFindings(unittest.TestCase):
    """Regression tests from the 2026-07-02 adversarial review. Each of
    these FAILED against the pre-review code — they discriminate."""

    def setUp(self):
        pygame.init()

    def tearDown(self):
        pygame.event.clear()
        pygame.quit()

    def test_cpu_tracks_max_deflection_edge_hit(self):
        """Finding B3: after a clamped corner hit, a descending ball has
        vy ≈ 0.45. The old idle check (vy < 0.5) made the CPU permanently
        blind to it — verified 3000 frames with zero CPU movement. The
        check must be a sign test, not a magnitude threshold."""
        cpu = CPU(difficulty=1.0)  # zero jitter — pure tracking
        ball = Ball()
        ball.x = 100
        ball.vy = 0.45  # legally descending, post-corner-hit
        paddle = Paddle(2, "bottom")  # centered at WINDOW_WIDTH/2
        move = cpu.get_move(paddle.rect, ball)
        self.assertEqual(move, "left",
            f"CPU ignored a slowly-descending ball (vy=0.45): got {move!r}")

    def test_unpause_during_serve_does_not_launch(self):
        """Finding R1: the resume keypress used to cascade into the
        any-key serve launcher — unpausing skipped the 5s countdown."""
        game = PongGame(mode="multiplayer")
        game.state = STATE_PAUSED
        self.assertGreater(game.ball.serve_delay, 0)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}))
        game.handle_input()
        self.assertEqual(game.state, STATE_SERVE, "Resume should return to the countdown")
        self.assertGreater(game.ball.serve_delay, 0, "Resume keypress launched the serve!")
        self.assertEqual(game.ball.vx, 0)
        self.assertEqual(game.ball.vy, 0)

    def test_r_during_confirm_quit_is_swallowed(self):
        """Finding R1: R during the confirm-quit dialog used to silently
        discard the dialog and instant-launch a fresh match."""
        game = PongGame(mode="multiplayer")
        game.state = STATE_CONFIRM_QUIT
        game.p1.score = 7
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_r}))
        game.handle_input()
        self.assertEqual(game.state, STATE_CONFIRM_QUIT, "Dialog was dismissed by R")
        self.assertEqual(game.p1.score, 7, "Match was reset from inside the quit dialog")

    def test_esc_on_win_exits_to_menu(self):
        """Finding R2: the win overlay says 'ESC = quit to menu' but ESC
        used to PAUSE the finished match — and resuming resurrected it."""
        game = PongGame(mode="multiplayer")
        game.state = STATE_WIN
        game.p1.score = 11
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
        game.handle_input()
        self.assertFalse(game.running, "ESC on win screen should exit the game loop")
        self.assertEqual(game._exit_target, "menu")

    def test_comeback_requires_actual_deficit(self):
        """Finding R4: the old low-score tracker was min(score, 0) == 0
        always, so ANY 11-10 win unlocked Comeback King — including one
        where the winner led 10-0 the whole way."""
        with tempfile.TemporaryDirectory() as tmp:
            with patch('achievements.ACHIEVEMENTS_FILE', os.path.join(tmp, "a.json")):
                game = PongGame(mode="multiplayer")
                game.achievements = AchievementManager()

                # Case 1: winner was at 10 when opponent hit 10 — no comeback.
                game.p1.score, game.p2.score = 11, 10
                game.p1_score_when_p2_hit_10 = 10
                game._trigger_win(winner_id=1)
                self.assertFalse(
                    game.achievements.achievements["comeback_king"]["unlocked"],
                    "Comeback King unlocked without a real deficit")

                # Case 2: winner was at 8 when opponent hit 10 — comeback.
                game2 = PongGame(mode="multiplayer")
                game2.achievements = game.achievements
                game2.p1.score, game2.p2.score = 12, 10
                game2.p1_score_when_p2_hit_10 = 8
                game2._trigger_win(winner_id=1)
                self.assertTrue(
                    game2.achievements.achievements["comeback_king"]["unlocked"],
                    "A genuine 8-10 comeback did not unlock")

    def test_tower_advance_shows_floor_intro(self):
        """The FLOOR {n} intro overlay only ever showed for floor 1 —
        advance_floor jumped straight to SERVE."""
        with tempfile.TemporaryDirectory() as tmp:
            with patch('achievements.ACHIEVEMENTS_FILE', os.path.join(tmp, "a.json")):
                game = PongGame(mode="tower")
                game.achievements = AchievementManager()
                game.advance_floor()
                self.assertEqual(game.current_floor, 2)
                self.assertEqual(game.state, STATE_TOWER_INTRO,
                    "Floor 2 should announce itself with the intro overlay")

    def test_tower_floor_5_milestone_unlocks(self):
        """Finding R5: check_tower_milestone was never called — Floor 5
        Conqueror was unobtainable despite tower mode shipping."""
        with tempfile.TemporaryDirectory() as tmp:
            with patch('achievements.ACHIEVEMENTS_FILE', os.path.join(tmp, "a.json")):
                game = PongGame(mode="tower")
                game.achievements = AchievementManager()
                game.current_floor = 4
                game.advance_floor()  # 4 -> 5
                self.assertTrue(
                    game.achievements.achievements["tower_floor_5"]["unlocked"],
                    "Reaching floor 5 did not unlock Floor 5 Conqueror")


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

    def test_exit_to_menu_does_not_tear_down_pygame(self):
        """Regression test: 'when I exit from a game it still exits the app
        instead of going to the start screen'. PongGame.run() used to call
        pygame.quit() unconditionally at the end -- including when the exit
        reason was 'menu', not 'quit the whole app'. pygame.quit() tears
        down the font/display modules, so the very next StartScreen.draw()
        call (which touches pygame.font) threw immediately. This test
        confirms pygame is still alive and the menu is still usable
        immediately after a game session ends with exit_target='menu'."""
        game = PongGame(mode="multiplayer")
        game.exit_to("menu")
        exit_target = game.run()
        self.assertEqual(exit_target, "menu")
        self.assertTrue(pygame.get_init(), "pygame was torn down on exit-to-menu")

        # The real symptom: does the menu actually still work afterward?
        menu = StartScreen()
        try:
            menu.draw(pygame.display.get_surface())
        except Exception as e:
            self.fail(f"Menu unusable after returning from a game: {e}")


if __name__ == "__main__":
    unittest.main()
