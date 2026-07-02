# Pong Tower — Mobile Port Spec (HTML5/JS)

**Decided:** 2026-07-02 by Daniel.
**Route:** HTML5/JavaScript canvas rewrite. Ship as a shareable link first
(GitHub Pages), wrap with Capacitor for app stores later.
**v1 scope:** Tower mode + 2-player local on one phone. Achievements port
in a later milestone (localStorage is ready for it).
**This file is the source of truth for the recorded port session.** The
pygame code stays the desktop reference implementation; nothing here
changes it.

---

## 1. Coordinate system & layout

- **Logical playfield: 700 wide × 1000 tall (portrait).** The desktop game
  is 1000×700 landscape with paddles on top/bottom; portrait is the same
  geometry rotated to fit a phone, and the top/bottom paddle layout is
  exactly right for two thumbs on one device.
- Render at logical coordinates, scale to fit the real screen with
  letterboxing (`scale = min(screenW/700, screenH/1000)`). Never read
  screen pixels directly in game logic.
- Ball bounces off LEFT/RIGHT walls; scores when it exits TOP (P2 point)
  or BOTTOM (P1 point). Same as desktop.

## 2. Physics — convert frame-based to time-based (dt)

Desktop logic assumes 60fps and moves per-frame. Phones run 60/90/120Hz,
so every speed becomes **units/second** (per-frame value × 60) and every
update is `pos += v * dt`.

| Constant | Desktop (per frame) | Mobile (per second) |
|---|---|---|
| Paddle speed | 7 | 420 |
| Ball start speed | 6 | 360 |
| Ball max speed | 18 | 1080 |
| Speed increment per paddle hit | 0.3 | 18 |
| Serve delay | 300 frames | 5.0 s |
| Tower intro | 90 frames | 1.5 s |
| Boost speed multiplier | 1.6× | 1.6× (unchanged, it's a ratio) |

Ball size (logical units, not time-based): start radius 18, min 5,
shrink 1.5 per paddle hit.

**Ball math (port verbatim from `ball.py`):**
- Serve: angle = ±90° from horizontal, ±30° random drift from vertical.
  Serve speed = startSpeed − (startRadius − radius) × 0.05×60, floor 240 u/s.
- Wall bounce: `angle = π − angle`.
- Paddle hit: `hitOffset = clamp((ball.x − paddle.centerX)/(paddle.width/2), −1, 1)`,
  `deflect = hitOffset × 1.5` (rad, ≈85° max).
  Top paddle: `angle = π/2 − deflect`. Bottom: `angle = −π/2 + deflect`.
  (Direction convention: right-edge hit sends ball right, both paddles.
  **This exact symmetry had an inverted-axis bug once — write the
  direction test FIRST, make it fail against a deliberately wrong sign.**
  See SKILLS.md "Agent Pitfalls".)
- After hit: speed += increment (cap max), radius −= shrink (floor min),
  reposition ball just outside paddle so it can't stick inside.
- Spin: +0.08 rad if the hitting paddle's boost is active.

## 3. State machine (port from `game.py`)

`serve (5s countdown) → playing → win` plus `paused → confirm_quit → menu`,
and tower-only: `tower_intro (1.5s) → serve`, `game_over` on CPU-mode loss.
Win score: 11. **Inputs must be gated by state** — paddles never move
while paused (known past bug class).

## 4. Tower mode & CPU (port from `cpu_opponent.py`)

- Floor difficulty: `min(0.3 + (floor−1) × 0.15, 0.95)` (floor 1 = 0.3,
  floor 5+ = 0.95).
- CPU error margin: `(1 − difficulty) × 60` logical px of noise added to
  its target x, re-rolled on a timer.
- CPU idles when ball is moving away from it (desktop check: `vy < 0.5`
  per-frame ⇒ mobile: `vy < 30` u/s).
- Advance one floor per match win; CPU drives the bottom paddle's normal
  move interface (no teleporting).

## 5. Touch controls (new design — the only genuinely new part)

- Screen split at the horizontal midline into two invisible touch zones.
- **Drag-follow:** paddle x tracks the finger's x while touching your
  zone, clamped to paddle max speed (so it feels physical, not teleporty).
- Tower mode: only the bottom zone is active (player is bottom paddle
  — note: desktop tower mode has the HUMAN as P1/top; flip so the human
  is the BOTTOM paddle on mobile — thumb ergonomics beat desktop parity).
- 2-player: one thumb each end, P1 top zone, P2 bottom zone. Multi-touch
  required (`touch-action: none`, track by `touch.identifier`).
- On-screen pause button (top corner), tap-outside-to-resume disabled;
  confirm-quit dialog as tap targets, min 44px.
- Keyboard input kept as a fallback so it's testable on desktop browsers.

## 6. Sound

Desktop generates .wav files with a synth script (`generate_sounds.py`).
Mobile: synthesize the same three cues (paddle hit, score, win) directly
with WebAudio oscillators — no audio files to load. **Audio context must
unlock on first user gesture** (mobile browser requirement) — init on
first touch of the start screen.

## 7. Persistence

localStorage. v1 stores nothing critical; achievement port (later
milestone) serializes the same JSON shape as `data/achievements.json`.

## 8. File plan

```
web/
  index.html      ← everything in one file for v1 (canvas, CSS, JS)
```
One file keeps deploy trivial. Split into modules only if it passes
~1500 lines.

## 9. Deployment (do BEFORE the recorded session)

1. GitHub repo → Settings → Pages → Deploy from branch → `master`, root.
2. Game URL becomes: `https://sobevista.github.io/Pong_Tower-Repo/web/`
3. Verify the URL serves a placeholder `web/index.html` before recording.

## 10. Recorded-session milestones (each one commits)

1. **M1** — canvas + letterbox scaling + dt game loop (spinning square proof).
2. **M2** — paddles + touch zones + drag-follow (test on real phone via Pages).
3. **M3** — ball physics + collisions + scoring (direction tests first).
4. **M4** — state machine + start screen + pause/confirm-quit.
5. **M5** — tower mode + CPU + floor ramp.
6. **M6** — WebAudio sound + polish (trail, glare, colors from settings.py).

Post-port backlog (desktop Phase 3 features, in this order): achievements,
paddle upgrades, power-ups, 4-player.

## 11. Definition of "ready to record"

- [ ] This spec merged and pushed
- [ ] GitHub Pages enabled and serving `web/index.html` placeholder
- [ ] Phone on hand for live testing during recording
- [ ] Desktop game verified playable at current commit (regression baseline)
