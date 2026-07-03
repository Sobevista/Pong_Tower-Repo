# Handoff to Hermes — 2026-07-03

**Commit:** pull latest on master (adversarial-review bugfix commit + PORT_SPEC rev 2)
**Summary:** An independent adversarial review subagent audited the whole
repo (code, tests, and PORT_SPEC.md). It found 3 blockers and 8 real
defects; all blockers and the high-value reals are now fixed and covered
by 7 new regression tests — each verified to FAIL against the old code
before the fix (per SKILLS.md "test what you claim").

## What changed (all on master)

- `cpu_opponent.py` — CPU idle check is now a sign test (`vy <= 0`), not
  a magnitude threshold. Old code went permanently blind to
  max-deflection edge hits (verified: 3000 frames, CPU never moved).
- `game.py` — input handlers no longer cascade (one keypress = one
  transition); ESC on win/game-over now actually exits to menu as the
  overlay promises; win-screen hint is mode-aware; Comeback King now
  tracks a real deficit (score when opponent hit 10) instead of a
  constant 0; tower floor milestones are wired; achievement popups
  display (stacked, no emoji tofu); floor intro shows on every floor;
  First Blood no longer awarded for CPU points; mixer init can't crash
  the game on machines without audio.
- `achievements.py` — check_tower_milestone returns newly-unlocked keys.
- `start_screen.py` — "MULTIPLIER" typo → "MULTIPLAYER".
- `test_pong.py` — 12 → 19 tests (TestAdversarialFindings class).
- `PORT_SPEC.md` — rev 2: fixed CPU sign-flip contradiction (§4/§5),
  completed the state machine (per-point serve loop was missing), floor
  difficulty examples corrected (floor 5 = 0.9), honest aspect-swap
  balance note, dt clamp + substep collision guards.

## Addendum (same day, Daniel's playtest feedback)

- Center dashed line is now HORIZONTAL (matches the top/bottom territory
  split) and paddles re-center on every serve. One new test (20 total).

## Known-and-deliberately-NOT-fixed (backlog, do not "fix" ad hoc)

- perfect_match and no_miss are the same condition (always unlock together)
- speed_demon implementation doesn't match its description
- max-deflection wall-crawl balance (80+ s rallies possible) — Daniel's
  tuning call after phone playtesting
- achievements file I/O: corrupt file silently resets progress; save() unguarded
- boost/wide/upgrade_level dead code — goes live with the power-up milestone

## Your job

1. `git pull origin master`.
2. `python -m unittest test_pong -v` — expect 19/19.
3. If you have a real display: play one tower match and one 2P match.
   Specifically try: pause during serve countdown → resume (should return
   to countdown, not launch); ESC on the win screen (should go to menu);
   an extreme edge hit vs the CPU (it should now chase it).
4. Report PARTIAL honestly if no display, as always.

## Open questions for Claude

None. Next Claude session = the recorded mobile-port session
(PORT_SPEC.md rev 2, milestones §10).
