# Pong Tower - Main Game Loop
# ============================
# Layout: paddles on TOP and BOTTOM, ball bounces LEFT/RIGHT
# P1 (top): A=left S=right  |  P2 (bottom): ;=left '=right

import pygame
import sys, random, math

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS, BACKGROUND_COLOR,
    CENTER_LINE_COLOR, PADDLE_MARGIN, WIN_SCORE, SCORE_FONT_SIZE,
    HUD_FONT_SIZE, WHITE, DARK_GRAY, GOLD, GREEN,
    SERVE_DELAY_FRAMES, PAUSE_KEY,
    HIT_SOUND_FILE, SCORE_SOUND_FILE, WIN_SOUND_FILE,
    HIT_VOLUME, SOUND_ENABLED, SOUND_DIR
)

from paddle import Paddle
from ball import Ball
from achievements import AchievementManager
from cpu_opponent import CPU

# ------------------------------------------------------------------
# Game States
# ------------------------------------------------------------------
STATE_SERVE = "serve"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_PAUSED = "paused"
STATE_TOWER_INTRO = "tower_intro"   # brief overlay showing floor before serve
STATE_GAME_OVER = "game_over"       # CPU tower defeat
STATE_CONFIRM_QUIT = "confirm_quit" # "Are you sure?" overlay during pause

# ------------------------------------------------------------------

# Resolve PAUSE_KEY string to actual pygame key constant
_key_map = {"SPACE": pygame.K_SPACE, "ESC": pygame.K_ESCAPE}
if isinstance(PAUSE_KEY, str):
    PAUSE_KEY = _key_map.get(PAUSE_KEY.upper(), pygame.K_SPACE)


def ball_health_color(radius, start, minimum):
    ratio = (radius - minimum) / max(1, start - minimum)
    if ratio > 0.6:
        return (100, 255, 100)
    elif ratio > 0.3:
        return (255, 255, 100)
    return (255, 100, 100)


class PongGame:
    def __init__(self, mode="multiplayer", starting_floor=1):
        self.mode = mode
        self.starting_floor = starting_floor
        self.current_floor = starting_floor
        self.floor_victories = 0  # wins on current floor (need 1 to advance for now)

        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", SCORE_FONT_SIZE, bold=True)
        self.hud_font = pygame.font.SysFont("consolas", HUD_FONT_SIZE)
        self.msg_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 48, bold=True)

        # Sound engine
        self.sounds = {}
        if SOUND_ENABLED:
            try:
                def _load(path):
                    if os.path.exists(path):
                        s = pygame.mixer.Sound(path)
                        s.set_volume(HIT_VOLUME)
                        return s
                    return None
                import os
                self.sounds["hit"] = _load(HIT_SOUND_FILE)
                self.sounds["score"] = _load(SCORE_SOUND_FILE)
                self.sounds["win"] = _load(WIN_SOUND_FILE)
            except Exception as e:
                print("Sound init warning:", e)

        self.achievements = AchievementManager()
        self.running = True
        self._exit_target = None

        # CPU (tower mode only)
        self.cpu = None
        if self.mode == "tower":
            # Difficulty ramps per floor: floor 1 = 0.3, floor 5 = 0.95
            diff = 0.3 + (self.current_floor - 1) * 0.15
            self.cpu = CPU(difficulty=min(diff, 0.95))

        self.reset_match()
        if self.mode == "tower":
            self.state = STATE_TOWER_INTRO
            self.intro_timer = 90  # 1.5s

    def reset_match(self):
        self.p1 = Paddle(1, "top")   # always human
        if self.mode == "tower" and self.cpu:
            self.p2 = Paddle(2, "bottom")
        else:
            self.p2 = Paddle(2, "bottom")
        self.ball = Ball()
        self.serve_direction = random.choice([-1, 1])
        self.ball.serve_delay = SERVE_DELAY_FRAMES
        self.winner_text = ""
        self.total_rallies = 0
        self.min_ball_radius_seen = self.ball.start_radius
        self.max_speed_seen = self.ball.start_speed
        self.p1_low_score = 0
        self.p2_low_score = 0
        self.popup_queue = []
        self.popup_timer = 0
        self.state = STATE_SERVE

    def advance_floor(self):
        self.current_floor += 1
        self.floor_victories = 0
        if self.cpu:
            diff = 0.3 + (self.current_floor - 1) * 0.15
            self.cpu.update_difficulty(min(diff, 0.95))
        self.reset_match()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                # --- Quit flow: Paused → Confirm → Menu ---
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_CONFIRM_QUIT:
                        self.state = STATE_PAUSED          # N: cancel quit
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_CONFIRM_QUIT   # 2nd Esc → confirm
                    else:
                        self.state = STATE_PAUSED          # 1st Esc during play

                if event.key == PAUSE_KEY:
                    if self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING if self.ball.serve_delay == 0 else STATE_SERVE
                    elif self.state == STATE_CONFIRM_QUIT:
                        self.state = STATE_PAUSED
                    elif self.state in (STATE_PLAYING, STATE_SERVE, STATE_TOWER_INTRO):
                        self.state = STATE_PAUSED

                if self.state == STATE_CONFIRM_QUIT:
                    if event.key == pygame.K_y:
                        self.exit_to("menu")
                    elif event.key == pygame.K_n:
                        self.state = STATE_PAUSED

                if event.key == pygame.K_r:
                    if self.state == STATE_WIN:
                        if self.mode == "tower":
                            self.advance_floor()
                        else:
                            self.reset_match()
                    elif self.state == STATE_GAME_OVER:
                        self.__init__(mode=self.mode, starting_floor=1)
                    else:
                        self.reset_match()

                if self.state == STATE_SERVE and self.ball.serve_delay > 0:
                    self.state = STATE_PLAYING
                    self.ball.serve(direction=self.serve_direction)

                if self.state == STATE_TOWER_INTRO:
                    self.state = STATE_SERVE

        # --- P1 (top) continuous movement ---
        if self.state not in (STATE_PAUSED, STATE_CONFIRM_QUIT):
            if keys[pygame.K_a]:
                self.p1.move_left()
            if keys[pygame.K_s]:
                self.p1.move_right()

        # --- P2 / CPU (bottom) movement ---
        if self.state not in (STATE_PAUSED, STATE_CONFIRM_QUIT):
            if self.mode != "tower":
                if keys[pygame.K_SEMICOLON]:
                    self.p2.move_left()
                if keys[pygame.K_QUOTE]:
                    self.p2.move_right()
            else:
                move = self.cpu.get_move(self.p2.rect, self.ball)
                if move == "left":
                    self.p2.move_left()
                elif move == "right":
                    self.p2.move_right()

    def update(self):
        if self.state == STATE_PAUSED:
            return
        if self.state == STATE_CONFIRM_QUIT:
            return

        if self.state == STATE_TOWER_INTRO:
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.state = STATE_SERVE
            return

        self.p1.tick()
        if self.mode != "tower":
            self.p2.tick()

        if self.state == STATE_SERVE:
            if self.ball.serve_delay > 0:
                self.ball.serve_delay -= 1
            else:
                self.state = STATE_PLAYING
                self.ball.serve(direction=self.serve_direction)

        elif self.state == STATE_PLAYING:
            self.ball.tick()

            self.min_ball_radius_seen = min(self.min_ball_radius_seen, self.ball.radius)
            self.max_speed_seen = max(self.max_speed_seen, self.ball.speed)
            self.p1_low_score = min(self.p1_low_score, self.p1.score)
            self.p2_low_score = min(self.p2_low_score, self.p2.score)

            ball_rect = self.ball.get_rect()

            # Top paddle collision (ball going up -> P1 hits)
            if self.ball.vy < 0 and self.p1.rect.colliderect(ball_rect):
                self.ball.on_paddle_hit(self.p1)
                self.total_rallies += 1
                self._play_sound("hit")

            # Bottom paddle collision (ball going down -> P2 hits)
            if self.ball.vy > 0 and self.p2.rect.colliderect(ball_rect):
                self.ball.on_paddle_hit(self.p2)
                self.total_rallies += 1
                self._play_sound("hit")

            if self.ball.is_out_top():
                self.p2.score += 1
                self.achievements.check_first_blood()
                self._play_sound("score")
                self._check_serve_reset(direction=-1)

            elif self.ball.is_out_bottom():
                self.p1.score += 1
                self.achievements.check_first_blood()
                self._play_sound("score")
                self._check_serve_reset(direction=1)

            if self.p1.score >= WIN_SCORE:
                self._trigger_win(winner_id=1)
            elif self.p2.score >= WIN_SCORE:
                if self.mode == "tower":
                    self._trigger_tower_game_over()
                else:
                    self._trigger_win(winner_id=2)

        elif self.state in (STATE_WIN, STATE_GAME_OVER):
            pass

        if self.popup_timer > 0:
            self.popup_timer -= 1

    def _check_serve_reset(self, direction):
        self.serve_direction = direction
        self.ball.reset()
        self.ball.serve_delay = SERVE_DELAY_FRAMES
        self.state = STATE_SERVE

    def _trigger_win(self, winner_id):
        self.state = STATE_WIN
        if winner_id == 1:
            self.winner_text = "P1 WINS"
            total = self.p1.score + self.p2.score
            self.achievements.check_perfect(self.p1.score, self.p2.score)
            self.achievements.check_no_miss(self.p2.score)
            self.achievements.check_comeback(self.p1_low_score, self.p2.score)
            self.achievements.check_shrink_master(self.min_ball_radius_seen)
            self.achievements.check_marathon(total)
            self.achievements.check_speed_demon(self.min_ball_radius_seen, self.max_speed_seen)
        else:
            self.winner_text = "P2 WINS"
            total = self.p1.score + self.p2.score
            self.achievements.check_perfect(self.p2.score, self.p1.score)
            self.achievements.check_no_miss(self.p1.score)
            self.achievements.check_comeback(self.p2_low_score, self.p1.score)
            self.achievements.check_shrink_master(self.min_ball_radius_seen)
            self.achievements.check_marathon(total)
            self.achievements.check_speed_demon(self.min_ball_radius_seen, self.max_speed_seen)

        self.achievements.check_first_win()
        self.achievements.check_rally_milestone(self.total_rallies)
        self.achievements.save()
        self._play_sound("win")

    def _trigger_tower_game_over(self):
        self.state = STATE_GAME_OVER
        self.winner_text = "CPU WINS"
        self._play_sound("win")

    def _play_sound(self, key):
        sound = self.sounds.get(key)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Vertical dashed center line
        dash_len = 20
        gap = 15
        cx = WINDOW_WIDTH // 2
        for y in range(0, WINDOW_HEIGHT, dash_len + gap):
            r = pygame.Rect(cx - 4, y, 8, dash_len)
            pygame.draw.rect(self.screen, CENTER_LINE_COLOR, r, border_radius=4)

        # Top/bottom border markers
        pygame.draw.line(self.screen, CENTER_LINE_COLOR, (0, 10), (WINDOW_WIDTH, 10), 2)
        pygame.draw.line(self.screen, CENTER_LINE_COLOR, (0, WINDOW_HEIGHT - 10), (WINDOW_WIDTH, WINDOW_HEIGHT - 10), 2)

        self.p1.draw(self.screen)
        self.p2.draw(self.screen)

        if self.state not in (STATE_WIN, STATE_GAME_OVER):
            self.ball.draw(self.screen)

        # Score
        surf1 = self.font.render(str(self.p1.score), True, self.p1.color)
        surf2 = self.font.render(str(self.p2.score), True, self.p2.color)
        self.screen.blit(surf1, (30, 20))
        self.screen.blit(surf2, (WINDOW_WIDTH - 30 - surf2.get_width(), 20))

        # Player labels
        p1_label = self.hud_font.render("P1  A LEFT   S RIGHT", True, self.p1.color)
        opponent_label = (
            f"CPU (FLOOR {self.current_floor})" if self.mode == "tower"
            else "P2  ; LEFT   ' RIGHT"
        )
        p2_label = self.hud_font.render(opponent_label, True, self.p2.color)
        self.screen.blit(p1_label, (10, WINDOW_HEIGHT - 30))
        self.screen.blit(p2_label, (WINDOW_WIDTH - 10 - p2_label.get_width(), WINDOW_HEIGHT - 30))

        # HUD: ball size + speed
        if self.state in (STATE_PLAYING, STATE_SERVE):
            size_label = f"Ball: {self.ball.radius:.1f}px  |  Speed: {self.ball.speed:.1f}"
            size_surf = self.hud_font.render(size_label, True, ball_health_color(
                self.ball.radius, self.ball.start_radius, self.ball.min_radius))
            self.screen.blit(size_surf, (WINDOW_WIDTH // 2 - size_surf.get_width() // 2, 10))

        # Tower intro overlay
        if self.state == STATE_TOWER_INTRO:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            fl = self.title_font.render(f"FLOOR {self.current_floor}", True, GOLD)
            self.screen.blit(fl, (WINDOW_WIDTH // 2 - fl.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            hint = self.hud_font.render("CPU activated — first to 11 wins   (any key to skip)", True, WHITE)
            self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, WINDOW_HEIGHT // 2 + 20))

        # Serve countdown
        if self.state == STATE_SERVE and self.ball.serve_delay > 0:
            secs = max(1, self.ball.serve_delay // FPS + 1)
            cd = self.msg_font.render(f"SERVE IN {secs}  |  any key to launch", True, WHITE)
            self.screen.blit(cd, (WINDOW_WIDTH // 2 - cd.get_width() // 2, WINDOW_HEIGHT // 2 - 40))

        # Confirm quit overlay
        if self.state == STATE_CONFIRM_QUIT:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            q = self.title_font.render("QUIT TO MENU?", True, GOLD)
            hs = self.hud_font.render("Y = yes   |   N / ESC = cancel", True, WHITE)
            self.screen.blit(q, (WINDOW_WIDTH // 2 - q.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(hs, (WINDOW_WIDTH // 2 - hs.get_width() // 2, WINDOW_HEIGHT // 2 + 20))

        # Pause (draw ONLY when not confirming — confirm is drawn above)
        if self.state == STATE_PAUSED:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            ps = self.title_font.render("PAUSED", True, GOLD)
            hs = self.hud_font.render("SPACE = resume   R = restart   ESC = quit", True, WHITE)
            self.screen.blit(ps, (WINDOW_WIDTH // 2 - ps.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(hs, (WINDOW_WIDTH // 2 - hs.get_width() // 2, WINDOW_HEIGHT // 2 + 20))

        # Win overlay (P1 victory)
        if self.state == STATE_WIN:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            ws = self.title_font.render(self.winner_text, True, GOLD)
            self.screen.blit(ws, (WINDOW_WIDTH // 2 - ws.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
            rs = self.hud_font.render("R = next floor   |   ESC = quit to menu", True, WHITE)
            self.screen.blit(rs, (WINDOW_WIDTH // 2 - rs.get_width() // 2, WINDOW_HEIGHT // 2))

        # Game over (CPU win)
        if self.state == STATE_GAME_OVER:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            ws = self.title_font.render(self.winner_text, True, GOLD)
            fl = self.hud_font.render(f"You reached floor {self.current_floor}", True, WHITE)
            rs = self.hud_font.render("R = restart tower   |   ESC = quit", True, WHITE)
            self.screen.blit(ws, (WINDOW_WIDTH // 2 - ws.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
            self.screen.blit(fl, (WINDOW_WIDTH // 2 - fl.get_width() // 2, WINDOW_HEIGHT // 2 - 10))
            self.screen.blit(rs, (WINDOW_WIDTH // 2 - rs.get_width() // 2, WINDOW_HEIGHT // 2 + 40))

        # Achievement popups
        if self.popup_timer > 0:
            for key in self.popup_queue:
                ach = self.achievements.achievements.get(key)
                if ach and ach.get("unlocked"):
                    pop = f"{ach['icon']}  {ach['name']}: {ach['description']}"
                    ps2 = self.hud_font.render(pop, True, GOLD)
                    self.screen.blit(ps2, (20, WINDOW_HEIGHT - 60))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            if self.state not in (STATE_PAUSED, STATE_CONFIRM_QUIT):
                self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        return self._exit_target

    def exit_to(self, target="menu"):
        self._exit_target = target
        self.running = False


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    from start_screen import StartScreen
    menu = StartScreen()
    clock = pygame.time.Clock()

    current_mode = None
    while True:
        # --- Menu phase ---
        if current_mode is None:
            selected_mode = None
            while selected_mode is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                selected_mode = menu.handle_input()
                menu.draw(screen)
                clock.tick(FPS)
            current_mode = selected_mode

        # --- Game phase ---
        game = PongGame(mode=current_mode)
        exit_target = game.run()

        # Game loop ended — check where we go
        if exit_target == "menu":
            current_mode = None   # back to menu
        else:
            break   # quit entirely
