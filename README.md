# Pong Tower

Retro Pong-with-a-tower-twist in Python/pygame — and the proving ground where the agent mesh went live: Claude + Hermes working the same repo through a protected master, CI truth machine, and the HANDOFF mailbox protocol.

## Entry ritual
Follow `RESUME.md`. Agents: read `HANDOFF.md` (the operating protocol) before touching anything.

## The rules that make this repo what it is
- `master` is protected (enforce_admins ON) — no direct pushes, from anyone. Branch → PR → `test` check green → Daniel merges.
- `tests/invariants/` is HUMAN-OWNED. Agents run them, never modify them. Red invariant = your change is wrong.
- Handoffs ride `HANDOFF_TO_HERMES.md` / `HANDOFF_TO_CLAUDE.md` — overwritten, never appended. The repo is the memory.

## Map
- Game: `game.py` + modules (`ball.py`, `paddle.py`, `cpu_opponent.py`, ...)
- Tests: `test_pong.py` + `tests/` (incl. `tests/invariants/`)
- Protocol: `HANDOFF.md`; history: `PROJECT_LOG.md`; next big thing: `PORT_SPEC.md` (mobile port)
