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
