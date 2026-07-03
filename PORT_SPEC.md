# Pong Tower — Mobile Port Spec (HTML5/JS)

**Decided:** 2026-07-02 by Daniel.
**Route:** HTML5/JavaScript canvas rewrite. Ship as a shareable link first
(GitHub Pages), wrap with Capacitor for app stores later.
**v1 scope:** Tower mode + 2-player local on one phone. Achievements port
in a later milestone (localStorage is ready for it).
**This file is the source of truth for the recorded port session.** The
pygame code stays the desktop reference implementation; nothing here
changes it.

> **Revision 2 (2026-07-03):** corrected after independent adversarial
> review + desktop bugfix commit. If a formula here disagrees with the
> code, the code at that commit wins — flag it, don't guess.

---

## 1. Coordinate system & layout

- **Logical playfield: 700 wide × 1000 tall (portrait).** Desktop is
  1000×700 landscape with paddles on top/bottom.
- **Honesty note: this is an aspect SWAP, not a rotation, and it changes
  balance.** Paddle travel lane shrinks 1000→700 (a 100-wide paddle now
  covers 14.3% of its lane vs 10% on desktop) and ball transit lengthens
  700→1000 (~43% more reaction time). The mobile game will play EASIER
  than desktop. Ship it, playtest, then tune (smaller paddle or faster
  ball) — don't pretend it's parity.
- Geometry constants (logical units): paddle 100×15, margin from edge 30,
  corner radius 6; ball start radius 18, min 5; CPU error margin 60
  (relatively larger on a 700-wide field — another "plays easier" factor).
- Render at logical coordinates, scale to fit the real screen with
  letterboxing (`scale = min(screenW/700, screenH/1000)`). Never read
  screen pixels in game logic.
- Ball bounces off LEFT/RIGHT walls; scores when it exits TOP (bottom
  player's point) or BOTTOM (top player's point). Same as desktop.

## 2. Physics — convert frame-based to time-based (dt)

Desktop logic assumes 60fps and moves per-frame. Phones run 60/90/120Hz,
so every speed becomes **units/second** (per-frame value × 60) and every
update is `pos += v * dt`.

**Two mandatory dt guards** (naive dt ports die without these):
1. **Clamp dt at 50 ms.** A tab-switch or GC hiccup can hand you a 500 ms
   frame; unclamped, the ball teleports.
2. **Substep collision:** if `speed * dt` exceeds the ball radius, split
   the move into N substeps so no single step exceeds one radius. At
   1080 u/s max speed, a single 50 ms step moves 54 units — straight
   through a 15-thick paddle. Desktop never hits this only because it's
   locked at 60fps.

| Constant | Desktop (per frame) | Mobile (per second) |
|---|---|---|
| Paddle speed | 7 | 420 |
| Ball start speed | 6 | 360 |
| Ball max speed | 18 | 1080 |
| Speed increment per paddle hit | 0.3 | 18 |
| Serve delay | 300 frames | 5.0 s |
| Tower intro | 90 frames | 1.5 s |

Ball size (logical units, not time-based): start radius 18, min 5,
shrink 1.5 per paddle hit.

**Ball math (port verbatim from `ball.py`):**
- Serve: vertical launch ±30° random drift; direction +1 = toward top,
  −1 = toward bottom. Serve speed: constant 360 u/s in practice (the
  radius-based formula in ball.py is dead code — radius resets to 18
  before every serve). Port it as the constant.
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
- Do NOT port: boost/spin (`boost_timer`, +0.08 rad) and wide-paddle —
  unreachable dead code on desktop (nothing ever activates them). They
  arrive with the power-up milestone, post-port.
- Known balance defect carried from desktop: near-max deflection produces
  very long wall-to-wall crawls (80+ s rallies observed). v1 ports it
  as-is for parity; the fix (lower max deflect to ~1.2 rad) is a tuning
  decision for Daniel after phone playtesting.

## 3. State machine (port from `game.py` — COMPLETE transition list)

States: `serve`, `playing`, `win`, `paused`, `confirm_quit`,
`tower_intro` (tower only), `game_over` (tower only). Win score: 11.

Transitions:
- `serve` —(5s elapses or any tap)→ `playing`
- `playing` —(point scored, no winner)→ `serve`  ← **fires on EVERY
  point; this loop was missing from rev 1 and would have shipped a
  one-serve game**
- `playing` —(a side reaches 11)→ `win` (human wins or 2P) / `game_over`
  (tower, CPU reaches 11)
- `win` —(R / tap)→ tower: next floor via `tower_intro`; 2P: rematch → `serve`
- `win` or `game_over` —(ESC / back)→ menu
- `game_over` —(R / tap)→ full tower restart at floor 1 → `tower_intro`
- `tower_intro` —(1.5s or any tap)→ `serve`; shows on EVERY floor
- any active state —(pause button)→ `paused` —(resume)→ back to the
  countdown if serve was pending, else `playing`
- `paused` —(quit)→ `confirm_quit` —(yes)→ menu / —(no)→ `paused`

**Input rules (bugs already fixed on desktop — do not reintroduce):**
one input event = one transition, never cascade a single tap through two
handlers (the resume tap must NOT also launch the serve); the confirm
dialog swallows every input except yes/no; paddles never move while
paused.

## 4. Tower mode & CPU (port from `cpu_opponent.py`)

- Floor difficulty: `min(0.3 + (floor−1) × 0.15, 0.95)` — floor 1 = 0.3,
  floor 5 = 0.9, cap 0.95 first binds at floor 6.
- CPU error margin: `(1 − difficulty) × 60` logical px of noise added to
  its target x, re-rolled every 15–45 frames (~0.25–0.75 s).
- **CPU idle check is a SIGN test relative to the CPU's own side** — this
  is direction-critical and rev 1 got it wrong:
  - Desktop (CPU on bottom): idle when `vy <= 0` (ball moving up/away).
  - Mobile (CPU on TOP, because the human takes the bottom paddle):
    idle when `vy >= 0` (ball moving down/away). **The sign flips with
    the side.** Never use a magnitude threshold (old `vy < 0.5` bug made
    the CPU permanently blind to max-deflection edge hits).
- Dead zone: no move when |paddle.centerX − targetX| < paddle.width × 0.3.
- Advance one floor per match win; CPU drives the paddle through the same
  move interface as a player (no teleporting). Tower milestones: floor 5
  and floor 10 unlock achievements (post-port milestone).

## 5. Touch controls (new design — the only genuinely new part)

- Screen split at the horizontal midline into two invisible touch zones.
- **Drag-follow:** paddle x tracks the finger's x while touching your
  zone, clamped to paddle max speed (so it feels physical, not teleporty).
- Tower mode: only the bottom zone is active — the human is the BOTTOM
  paddle on mobile (thumb ergonomics; note this flips desktop, where the
  human is P1 on top — hence the CPU sign flip in §4).
- 2-player: one thumb each end, P1 top zone, P2 bottom zone. Multi-touch
  required (`touch-action: none`, track by `touch.identifier`).
- On-screen pause button (top corner); confirm-quit dialog as tap
  targets, min 44px. Keyboard kept as fallback for desktop browsers.

## 6. Sound

Desktop generates .wav files with a synth script (`generate_sounds.py`).
Mobile: synthesize the same three cues (paddle hit, score, win) directly
with WebAudio oscillators — no audio files to load. **Audio context must
unlock on first user gesture** (mobile browser requirement) — init on
first touch of the start screen. If audio init fails, the game plays
silent — never crash on missing audio (desktop learned this the hard way).

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
   (verify — repo name casing must match exactly).
3. Verify the URL serves the placeholder `web/index.html` before recording.

## 10. Recorded-session milestones (each one commits)

1. **M1** — canvas + letterbox scaling + clamped/substepped dt loop
   (spinning square proof).
2. **M2** — paddles + touch zones + drag-follow (test on real phone via Pages).
3. **M3** — ball physics + collisions + scoring (direction tests first).
4. **M4** — full state machine (§3 list is the checklist) + start screen.
5. **M5** — tower mode + CPU (§4 sign flip!) + floor ramp + per-floor intro.
6. **M6** — WebAudio sound + polish (trail, glare, colors from settings.py).

Post-port backlog (desktop Phase 3 features, in this order): achievements
(+ the popup UI), paddle upgrades, power-ups (boost/spin/wide go live
here), 4-player.

## 11. Definition of "ready to record"

- [ ] This spec (rev 2) merged and pushed
- [ ] GitHub Pages enabled and serving `web/index.html` placeholder
- [ ] Phone on hand for live testing during recording
- [ ] Desktop game verified playable at the bugfix commit (regression
      baseline — 19/19 tests green, both modes smoke-tested)
