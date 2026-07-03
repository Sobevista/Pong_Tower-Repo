# Pong Tower - Achievements
# =========================

import json
import os
from settings import DATA_DIR

ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, "achievements.json")

# All possible achievements with their trigger conditions
# tracked by name + description
DEFAULT_ACHIEVEMENTS = {
    "first_blood": {
        "name": "First Blood",
        "description": "Score your first point",
        "icon": "🍒",
        "unlocked": False
    },
    "perfect_match": {
        "name": "Perfect Match",
        "description": "Win a game 11-0",
        "icon": "🌟",
        "unlocked": False
    },
    "speed_demon": {
        "name": "Speed Demon",
        "description": "Win a rally where ball was at minimum size",
        "icon": "⚡",
        "unlocked": False
    },
    "marathon": {
        "name": "Marathon",
        "description": "Win a game with 30+ total points scored",
        "icon": "🏃",
        "unlocked": False
    },
    "comeback_king": {
        "name": "Comeback King",
        "description": "Win after being down 8-10",
        "icon": "👑",
        "unlocked": False
    },
    "shrink_master": {
        "name": "Shrink Master",
        "description": "Win a game where ball shrank below 8 radius",
        "icon": "🔻",
        "unlocked": False
    },
    "rally_100": {
        "name": "Rally Century",
        "description": "Hit 100 total rally shots",
        "icon": "💯",
        "unlocked": False
    },
    "first_win": {
        "name": "First Victory",
        "description": "Win your first full game",
        "icon": "🏆",
        "unlocked": False
    },
    "no_miss": {
        "name": "Clean Sweep",
        "description": "Win without conceding a single point",
        "icon": "🧹",
        "unlocked": False
    },
    "affix_survivor": {
        "name": "Affix Survivor",
        "description": "Win a match with 2 active affixes",
        "icon": "💀",
        "unlocked": False
    },
    "tower_floor_5": {
        "name": "Floor 5 Conqueror",
        "description": "Reach floor 5 of Pong Tower",
        "icon": "🗼",
        "unlocked": False
    },
    "tower_conqueror": {
        "name": "Tower Conqueror",
        "description": "Clear the full Pong Tower",
        "icon": "🏰",
        "unlocked": False
    }
}


class AchievementManager:
    def __init__(self):
        self.achievements = self._load()

    def _load(self):
        if os.path.exists(ACHIEVEMENTS_FILE):
            try:
                with open(ACHIEVEMENTS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {k: dict(v) for k, v in DEFAULT_ACHIEVEMENTS.items()}

    def save(self):
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump(self.achievements, f, indent=2)

    def unlock(self, key: str):
        """Unlock an achievement if not already unlocked. Returns True if newly unlocked."""
        if key not in self.achievements:
            return False
        if not self.achievements[key]["unlocked"]:
            self.achievements[key]["unlocked"] = True
            self.save()
            return True
        return False

    def get_unlocked(self):
        return [k for k, v in self.achievements.items() if v["unlocked"]]

    def get_total_count(self):
        return len(self.get_unlocked())

    # ---- Trigger helpers ----
    def check_first_blood(self):
        return self.unlock("first_blood")

    def check_first_win(self):
        return self.unlock("first_win")

    def check_perfect(self, my_score, opponent_score):
        if my_score == 11 and opponent_score == 0:
            return self.unlock("perfect_match")
        return False

    def check_no_miss(self, my_conceded):
        if my_conceded == 0:
            return self.unlock("no_miss")
        return False

    def check_comeback(self, my_score_at_low, opponent_score_at_high):
        if my_score_at_low <= 8 and opponent_score_at_high >= 10:
            return self.unlock("comeback_king")
        return False

    def check_shrink_master(self, min_ball_radius):
        if min_ball_radius < 8:
            return self.unlock("shrink_master")
        return False

    def check_marathon(self, total_points):
        if total_points >= 30:
            return self.unlock("marathon")
        return False

    def check_rally_milestone(self, total_hits):
        if total_hits >= 100:
            return self.unlock("rally_100")
        return False

    def check_speed_demon(self, min_ball_radius, rally_speed):
        if min_ball_radius <= 6 and rally_speed >= 14:
            return self.unlock("speed_demon")
        return False

    def check_tower_milestone(self, floor):
        """Returns the list of keys newly unlocked by reaching this floor,
        so the caller can show popups for exactly those."""
        newly = []
        if floor >= 5 and self.unlock("tower_floor_5"):
            newly.append("tower_floor_5")
        if floor >= 10 and self.unlock("tower_conqueror"):
            newly.append("tower_conqueror")
        return newly

    def check_affix(self, active_count):
        if active_count >= 2:
            return self.unlock("affix_survivor")
        return False
