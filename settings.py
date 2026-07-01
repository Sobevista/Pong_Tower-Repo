# Pong Tower - Core Settings
# ===========================

import os

# --- Display ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Pong Tower"
FPS = 60
BACKGROUND_COLOR = (10, 10, 20)
CENTER_LINE_COLOR = (40, 40, 60)

# --- Paddles ---
# Layout: paddles on TOP and BOTTOM, moving LEFT/RIGHT
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 7
PADDLE_MARGIN = 30                     # distance from top/bottom edge
PADDLE_COLOR_P1 = (0, 200, 255)        # cyan — top paddle
PADDLE_COLOR_P2 = (255, 80, 80)        # red  — bottom paddle
PADDLE_CORNER_RADIUS = 6

# --- Ball ---
BALL_START_RADIUS = 18
BALL_MIN_RADIUS = 5
BALL_START_SPEED = 6
BALL_MAX_SPEED = 18
BALL_SHRINK_PER_HIT = 1.5
BALL_SPEED_INCREMENT = 0.3
BALL_SPIN_FACTOR = 0.08
BALL_COLOR = (255, 255, 200)
BALL_TRAIL_ALPHA = 60

# --- Score ---
WIN_SCORE = 11
SCORE_FONT_SIZE = 72
HUD_FONT_SIZE = 18

# --- Colors ---
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 40)
GOLD = (255, 215, 0)
GREEN = (80, 220, 100)

# --- Audio ---
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
HIT_SOUND_FILE = os.path.join(SOUND_DIR, "paddle_hit.wav")
SCORE_SOUND_FILE = os.path.join(SOUND_DIR, "score.wav")
WIN_SOUND_FILE = os.path.join(SOUND_DIR, "win.wav")
SOUND_ENABLED = True
HIT_VOLUME = 0.5

# --- Serve ---
SERVE_DELAY_FRAMES = 300               # 5 seconds at 60fps

# --- Pause ---
PAUSE_KEY = "SPACE"

# --- Directory ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR = os.path.join(PROJECT_DIR, "saves")
DATA_DIR = os.path.join(PROJECT_DIR, "data")

os.makedirs(SAVES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SOUND_DIR, exist_ok=True)
