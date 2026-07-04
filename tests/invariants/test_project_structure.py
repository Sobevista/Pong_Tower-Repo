# Pong Tower - PROJECT STRUCTURE INVARIANT (human-owned, agent-read-only)
# =======================================================================
# The project must not lose its own source files. This exists because a
# mounted-folder git index corruption once staged the entire game for
# deletion (see Dump_Agent_Swarm V7 incident + cowork-mount-survival).
# If a commit ever drops a core module, THIS goes red immediately —
# the truth machine catches the deletion instead of it slipping through.

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CORE_MODULES = [
    "game.py",
    "ball.py",
    "paddle.py",
    "settings.py",
    "cpu_opponent.py",
    "achievements.py",
    "start_screen.py",
    "test_pong.py",
]


class ProjectStructureInvariant(unittest.TestCase):
    def test_core_modules_present(self):
        missing = [m for m in CORE_MODULES if not (REPO_ROOT / m).is_file()]
        self.assertEqual(
            missing, [], f"Core source files missing from repo: {missing}"
        )

    def test_core_modules_not_truncated(self):
        # A zero-byte core file is the signature of a truncated/corrupted write.
        empty = [
            m
            for m in CORE_MODULES
            if (REPO_ROOT / m).is_file() and (REPO_ROOT / m).stat().st_size == 0
        ]
        self.assertEqual(
            empty, [], f"Core source files are empty (possible truncation): {empty}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
