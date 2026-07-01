# Pong Tower - Test Suite
import unittest
import pygame
import math
from unittest.mock import patch, MagicMock
from game import PongGame, STATE_PLAYING, STATE_PAUSED
from paddle import Paddle

class TestPongGame(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = PongGame(mode="multiplayer")
        
    def tearDown(self):
        pygame.quit()
        
    def test_paddle_no_move_during_pause(self):
        self.game.state = STATE_PAUSED
        initial_x = self.game.p1.rect.x
        
        # Mock key press: 'A' held down
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

if __name__ == "__main__":
    unittest.main()
