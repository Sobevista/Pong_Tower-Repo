# RESUME — entry point
*"Follow RESUME.md" lands here. Chassis seeded 2026-07-11 (R1 rollout).*

## What this is
Pong Tower — pygame retro game AND the live proving ground of the agent mesh (Claude + Hermes + Daniel-as-merge-gate). The protocol that runs this repo is `HANDOFF.md`; read it first if you're an agent.

## Cold start (repo layer)
1. Clone: `gh repo clone Sobevista/Pong_Tower-Repo "$HOME\Repos\Pong_Tower-Repo"`
2. Install: `python -m pip install pygame pytest`
3. Verify the truth machine locally: `python -m pytest -v tests/invariants/` then `python -m pytest -v test_pong.py` (always `python -m pytest`, never bare `pytest`). CI runs the same as the `test` check.
4. Read the newest `HANDOFF_TO_*.md` — that's the current hop — then `PROJECT_LOG.md` if you need history.

No secrets required. Note for Claude sessions: the sandbox has no display/audio — anything feel-related must go to Hermes via the handoff.

## Where things stand
Default branch: `master` (protected; fleet-wide rename to `main` is queued in the harness Command_Card — if this line is stale and the branch is `main`, trust the branch list). Current work: mobile port, `PORT_SPEC.md` rev 2.
