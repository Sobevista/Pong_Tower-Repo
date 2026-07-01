# Project Log: Pong Tower

**Root Directory:** C:\Users\dansl\PONG_GAME\
**Last Session Date:** 2026-07-01
**Tech Stack:** Python 3.11 + Pygame 2.6.1 (Hermes venv)

---

## Map (Where We Live In The Build)

```
Phase 1 — Foundation          ▼ DONE
  ├─ Top/bottom paddles
  ├─ Ball: shrink, speed, trail, angle deflection
  ├─ 2-player controls
  ├─ Auto-serve (5s), pause
  ├─ 12 achievements + JSON persistence
  └─ Sound engine (generated .wav)

Phase 2 — Structure          ▼ DONE
  ├─ Start screen + mode select
  ├─ CPU opponent (tracks ball, difficulty ramps per floor)
  ├─ Tower mode: floor intro, advance on win
  └─ Pause -> confirm quit -> menu flow

Phase 3 — Stacking           ← NEXT
  ├─ Multiplayer 4-player input (IJKL + Numpad)
  ├─ Paddle upgrade system (speed, wide, shield)
  └─ Power-up spawning system

Phase 4 — RPG Layer
  ├─ XP per floor cleared
  ├─ Unlockable paddles/affixes
  └─ Player profile save/load

Phase 5 — Affix System
  ├─ Random affix engine (1-2 per floor)
  └─ Affix types: Champion, Spiteful, Grievous, Bomb

Phase 6 — Pong Tower
  ├─ 5-10 floors, escalating difficulty
  ├─ Floor transitions, tower completion
  └─ Final achievement unlocks
```

---

## What Just Changed

**Bugs fixed this session:**
1. Menu arrow no longer vibrates — smooth slow pulse
2. CPU is now active in tower mode (mode string was mismatched: menu returned `"PONG TOWER"` but game routed on `"tower"`)
3. CPU only reacts when ball is coming toward it, idles when ball is going away
4. Pause flow is now: Esc → Pause → Esc → "Are you sure?" → Y = menu, N = back to pause
5. Menu selection returns clean mode keys: `"tower"` or `"multiplayer"`

**New files:**

| File | Purpose |
|---|---|
| `start_screen.py` | Mode select menu |
| `cpu_opponent.py` | CPU with difficulty 0.3 → 0.95 per floor |

---

## Current State

**Run it:**
```bash
python game.py
```

**Flow:**
1. Start screen → select Tower or Multiplier
2. Tower: floor intro overlay (1.5s) → play vs CPU → win = next floor
3. Multiplier: local P1 vs P2
4. Pause → Space or Esc
5. Quit → Esc while paused → "Y to menu / N back"

**Controls:**
- P1: A / S
- P2: ; / '
- Space: pause/resume
- Esc: pause → confirm → menu
- R: restart

---

## Session: Claude review + fix pass (verified via GitHub, headless sandbox)

**Confirmed and fixed — bottom-paddle deflection was still inverted after the prior commit.**
The previous fix (`FIX: Normalize serve direction semantics + bottom paddle deflection`)
changed vy's sign correctly but kept vx inverted: hitting the right edge of the
bottom paddle sent the ball LEFT instead of RIGHT. The existing regression test
only checked `vy < 0` (bounced up at all), never checked `vx` direction relative
to hit offset — so it passed the whole time. Root cause: `ball.py`'s
`on_paddle_hit` used `-math.pi/2 - deflect` for the bottom paddle; correct form
is `-math.pi/2 + deflect` to mirror the top paddle's (correct) behavior.

Added 3 new tests (`test_bottom_paddle_right_edge_deflects_right`,
`test_bottom_paddle_left_edge_deflects_left`, `test_top_bottom_deflection_symmetry`)
that check vx sign explicitly — the exact thing the old suite missed.

**Other cleanup:**
- Removed redundant identical if/else branch in `reset_match()` (both paths
  did the same thing — leftover from an incomplete patch)
- `CPU.reaction_speed` was computed but never used in `get_move()` — removed
  and left a note that a real reaction-lag mechanic would be a good next step
  for making higher floors feel harder (not just more accurate)
- `Paddle.get_current_width()` / `wide_timer` / `apply_wide()` are scaffolding
  with zero call sites and no effect on `self.rect` or collision — left in
  place but clearly commented as unwired, so it doesn't look finished when
  it isn't

**Verification method:** all 7 tests pass headless (`SDL_VIDEODRIVER=dummy`),
plus a 300-frame smoke run in both `multiplayer` and `tower` modes to catch
runtime issues that `py_compile` alone wouldn't (this bit the project
multiple times earlier in the build — files that compiled clean but crashed
on first real frame).

**Workflow note:** this was done by pulling the repo directly via git
(read/write access, scoped fine-grained PAT) rather than via pasted
transcripts or re-uploaded files — first real test of the shared-repo,
two-agent loop described in the Git Workflow section of SKILLS.md.

