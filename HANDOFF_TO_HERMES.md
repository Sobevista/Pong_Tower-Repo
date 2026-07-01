# Handoff to Hermes — 2026-07-01

**Commit:** c733d4e on master
**Summary:**
- Fixed a real bug: bottom-paddle deflection from an earlier commit was
  still inverted horizontally — right-edge hits sent the ball left instead
  of right. Verified numerically, fixed in `ball.py`.
- Added 3 tests in `test_pong.py` checking `vx` direction, not just `vy`
  sign — the old test's blind spot is exactly why the bug shipped once
  already.
- Collapsed a redundant branch in `reset_match()`, removed an unused field
  in `cpu_opponent.py`, commented the unwired wide-paddle scaffolding in
  `paddle.py` so it doesn't read as finished when it isn't.
- Added `HANDOFF.md` — this file and `HANDOFF_TO_CLAUDE.md` are now the
  standing two-way handoff mechanism. Read that file for the full protocol.

## Your job

1. `git pull origin master`
2. Read the "Agent Pitfalls" additions in `SKILLS.md` (direction-testing,
   headless smoke tests) before touching anything
3. Run `python -m unittest test_pong -v` in the real venv — confirm all 7
   pass (not just the 3 new ones)
4. Run `python game.py` for real — actual display, actual keyboard input,
   actual audio. Play both Tower and Multiplayer modes. Specifically hit
   the bottom paddle on its right edge and left edge a few times each and
   confirm the ball deflects the way it should now (right hit → right,
   left hit → left) — this is the one thing that can't be confirmed from
   a headless sandbox
5. Confirm the pause → confirm-quit → menu flow still works end-to-end
   with real key events (Claude's tests simulate this via `pygame.event`,
   but real OS-level key repeat/timing can behave differently)

## What Claude could NOT verify

Everything here was confirmed via headless sandbox (`SDL_VIDEODRIVER=dummy`)
and simulated event injection — the math is right, the state transitions
are right in isolation, but none of it has been played by a human with
real input latency, real audio output, or real display timing. That's
entirely your side of this loop.

## If something's broken

Fix it, add a regression test for whatever you find (see the new pitfall
notes in `SKILLS.md`), commit, push, and write it up plainly in
`HANDOFF_TO_CLAUDE.md` — evidence, not just a verdict. If everything
checks out clean, say that plainly too, with what you actually did to
confirm it (which mode, how many hits tested, etc.) — not just "tested and
confirmed."
