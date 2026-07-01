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

## Agent Pitfalls
- **Patching:** Avoid redundant patches. If logic is complex, rewrite the whole block or function.
- **State Logic:** Ensure input handlers check `game.state` before updating paddle positions.
- **Dependency:** Verify libraries are in the local venv before assuming existence.
