# Pong Tower — Build Outline
*Thin by design (added at the 2026-07-11 R1 chassis rollout): this repo predates the chassis and already carries its state in `PROJECT_LOG.md` (historical log) and `HANDOFF_TO_*.md` (current hop). This file indexes them instead of duplicating them — one home per fact.*

## LOCKED
- HANDOFF protocol (`HANDOFF.md`): two-agent loop, mailbox files overwritten not appended, last commit of a session = the handoff update.
- Protected master + CI `chassis/phase0` (runs `tests/invariants/` then `test_pong.py`, headless). Neither agent merges its own PR.
- `tests/invariants/` human-owned.

## OPEN
- **Mobile port** — spec in `PORT_SPEC.md` (rev 2). The current phase of work.
- Known debt: `HANDOFF.md` hardcodes `cd C:\Users\dansl\PONG_GAME` (same pet-path class the fleet killed in R4/LiftLens PR #12) — replace with the clone-or-pull block when HANDOFF is next touched.

## STATE OF BUILD
Live state = `PROJECT_LOG.md` (history) + the newest `HANDOFF_TO_*.md` (current hop) — read those, not this file, for where work actually is.
- **2026-07-11 (pm)** — Chassis seeded (README + this file + RESUME) per R1 rollout; content deliberately points at the repo's existing conventions. **NEXT ACTION: mobile port per `PORT_SPEC.md` rev 2.**
