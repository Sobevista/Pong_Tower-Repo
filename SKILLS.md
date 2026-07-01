# PONG_GAME SKILLS.md

## Project Conventions
- **Coordinate System:** Pygame Y-down (0,0 is top-left).
- **Physics Math:** Use radians. Sin/Cos for ball velocity vectors.
- **Python Environment:** Use C:\Users\dansl\AppData\Local\Programs\Python\Python314\python.exe.
- **State Pattern:** Game must gate inputs during pause states to prevent paddle movement/illegal inputs.

## Git Workflow
- Commit after every milestone (bug fix, new feature, state transition).
- Commit messages: [ACTION] Brief summary.
- Branching: Keep on `master` for now; use `git checkout -b` for experimental spikes.
- **Shared repo:** This remote is the source of truth for multi-agent work. After every verified commit, push: `git push origin master`.
- **Handoff files:** last commit of every session should update `HANDOFF_TO_HERMES.md` or `HANDOFF_TO_CLAUDE.md` (whichever direction applies). See `HANDOFF.md` for the full protocol. This is how the other agent knows what to do next without Daniel manually relaying it.

## Agent Pitfalls
- **Patching:** Avoid redundant patches. If logic is complex, rewrite the whole block or function.
- **State Logic:** Ensure input handlers check `game.state` before updating paddle positions.
- **Dependency:** Verify libraries are in the local venv before assuming existence.
- **Test what you claim, not what's convenient:** a test that checks `vy < 0` ("did it bounce") is not the same as testing `vx` direction relative to hit offset ("did it bounce the *right way*"). A prior bottom-paddle deflection fix passed its own test while still being inverted on the horizontal axis, because the test only checked the easy half. When fixing a symmetry/direction bug, write the test to fail against the *old* code first, not just pass against the new code.
- **`py_compile` passing ≠ working:** run a real headless frame loop (`SDL_VIDEODRIVER=dummy`) for a few hundred frames before calling something verified. Multiple bugs in this project's history compiled clean but crashed or misbehaved on first actual play.
