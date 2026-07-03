# Project Log: Pong Tower

**Root Directory:** C:\Users\dansl\PONG_GAME\
**Last Session Date:** 2026-07-03
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

Phase 2.5 — Hardening        ▼ DONE (2026-07-03)
  ├─ Adversarial review (independent subagent): 3 blockers, 8 reals
  ├─ CPU edge-hit blindness fixed; input cascade fixed; ESC-on-win fixed
  ├─ Comeback/1st-blood/tower milestones/popups fixed; audio crash guard
  ├─ Horizontal center line; paddles re-center per serve (playtest)
  └─ Test suite 12 → 20, all proven to fail against pre-fix code

Phase M — Mobile Port        ▼ v1 DONE (2026-07-03, not recorded)
  ├─ HTML5/JS canvas, portrait 700×1000, single-file web/index.html
  ├─ M1–M6 all in: letterbox+dt loop, touch drag-follow, ball physics,
  │   state machine, tower/CPU (sign flip), WebAudio synth
  ├─ Touch controls: split-zone drag-follow (bottom=human in tower, both in 2P)
  ├─ Stats & Awards screen added early (achievements now viewable) + localStorage
  └─ Verified headless: 21 logic tests + all-states/300-frame render smoke

Phase 3 — Stacking           (after mobile port)
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

---

## Session: Web port v1 (2026-07-03, port session, NOT recorded)

Built the full HTML5/JS port in a single `web/index.html` per PORT_SPEC rev 2.
Decision this session: skip recording (the repo IS the record); scope = port +
a basic stats screen so the already-firing achievements have somewhere to live.

**Shipped:**
- Logical 700×1000 portrait field, letterbox scaling, dt loop with the two
  mandatory guards (50ms clamp + substep collision — verified a max-speed ball
  is caught, not tunneled, by the 15-thick paddle).
- Touch controls (the only genuinely new part): split-zone drag-follow clamped
  to paddle max speed; tower = bottom zone only (human is BOTTOM on mobile);
  2P = both zones, multi-touch by identifier. Keyboard kept as desktop fallback.
- Ball physics ported verbatim (serve ±30°, wall bounce, paddle deflect ±1.5rad,
  shrink/speed-up, burst-outside). Direction tests written FIRST and pass.
- CPU sign flip handled: CPU is TOP, idles when vy≥0 (ball moving away). Tested
  against the old magnitude-threshold bug.
- Full state machine incl. the per-point serve loop that rev1 nearly dropped.
- WebAudio synth (no files), unlocks on first gesture, silent-safe.
- **Stats & Awards screen**: highest floor, floors cleared, games won, longest
  rally, total rally hits, and all 12 achievements (earned/locked). localStorage.

**Verification:** 21 headless logic assertions (paddle-hit axis both edges, CPU
sign flip, serve direction, substep no-tunnel, scoring loop, win/game-over,
floor-difficulty ramp) + a render smoke over every state and 300 tower frames.
Mount truncation bit us again mid-build (file-tool write landed 12 lines on the
shell side) — caught by the sentinel check, force-rewritten via bash, md5 now
matches host. cowork-mount-survival earned its keep.

---

## BACKLOG — carried forward, do NOT lose (MVP+ features)

These fire/exist but have gaps. Explicit here so they survive across threads:

1. **Persistent cross-device user profile.** Today stats/achievements live in
   browser localStorage — per-device, cleared if cache is wiped. Daniel wants a
   real profile to check his stats. Needs: an identity (even just a name/PIN) and
   a backend or synced store so the kids' tablet and his machine share progress.
2. **Full stats page (desktop parity + history).** The web Stats screen is a v1;
   extend with per-floor bests, win/loss record, session history, achievement
   dates.
3. **Leaderboard.** No leaderboard anywhere yet. Local (per-device high scores)
   is the cheap first step; global needs the backend from item 1.
4. Desktop achievements were firing (floor 5, rally 100) with NO in-game place to
   view them — the web Stats screen closes that on mobile; do the same on desktop
   (pygame profile/stats screen) when convenient.

(Existing PORT_SPEC §10 post-port backlog still stands: achievement popups polish,
paddle upgrades, power-ups, 4-player.)
