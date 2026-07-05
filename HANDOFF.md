# Handoff Protocol

This repo is worked on by two agents — Claude (via direct git read/write,
pulling this repo fresh each session) and Hermes (running locally on
Daniel's machine with real display/audio/input access, which Claude's
sandbox does not have).

Neither agent has memory between sessions. This repo *is* the memory.
Two files carry state between hops instead of Daniel manually relaying
prose back and forth:

- **`HANDOFF_TO_HERMES.md`** — written by Claude, last thing before ending
  a session. Overwritten each time (not appended) — only the latest handoff
  matters, git history already has everything before it.
- **`HANDOFF_TO_CLAUDE.md`** — written by Hermes, same rule, overwritten
  each time.

## The loop

1. Claude pulls latest master, reviews/fixes/builds on a branch, commits,
   pushes the branch, opens a PR (`gh pr create --base master`), and
   updates `HANDOFF_TO_HERMES.md` (on that same branch/PR) as the final
   commit of the session. See "Workflow: branch → PR → CI → human merge"
   above — Claude does not push to master directly.
2. Daniel merges the PR once the `test` check is green, then tells Hermes
   to pull master and read `HANDOFF_TO_HERMES.md`.
3. Hermes does whatever that file asks — usually: run the real thing with
   real I/O, since that's the one capability Claude's sandbox doesn't have.
4. Hermes works on its own branch, commits, pushes the branch, opens a PR,
   and updates `HANDOFF_TO_CLAUDE.md` as its final commit — same rule,
   no direct push to master.
5. Daniel merges Hermes's PR once green, then tells Claude to pull master
   and read `HANDOFF_TO_CLAUDE.md`. Repeat.

Daniel's role in each direction is just "go tell the other one to pull" —
not retyping content. If a handoff file is asking him to relay a decision
or a preference only he can make, that's fine and expected; what shouldn't
happen is him manually copying technical findings between the two.

## Workflow: branch → PR → CI → human merge

`master` is protected (`enforce_admins` on) — **direct pushes to master are
physically blocked**, for both agents and Daniel. There is no "just push it"
path anymore. Every change, from either agent, follows this shape:

1. Branch off up-to-date `master` (`git checkout -b <name>`).
2. Commit, push the branch (`git push -u origin <name>`).
3. Open a PR into master: `gh pr create --base master`.
4. Wait for the `test` status check (the `chassis/phase0` CI: runs
   `tests/invariants/` then `test_pong.py`, headless, on every push to a
   non-master branch and every PR into master) to go green.
5. A human (Daniel) merges the PR. Neither agent merges its own PR.

Two things that ride along with this:

- **`tests/invariants/` is human-owned.** Agents may run these tests, never
  modify them. If a change makes an invariant go red, the change is wrong,
  not the test — fix the change, don't touch the test. See
  `tests/invariants/README.md`.
- **The mount-safety pre-commit hook is wired in** (`core.hooksPath` is set
  to `.githooks`). It blocks any commit that deletes one of the 8 core
  source files, or removes 5+ tracked files at once — the corrupted
  mounted-folder-index failure mode. Bypass with `git commit --no-verify`
  only when the deletion is genuinely intentional.

## Format: HANDOFF_TO_HERMES.md (Claude → Hermes)

```markdown
# Handoff to Hermes — <date>

**Commit:** <short hash> on master
**Summary:** <2-4 bullets, terse, what actually changed>

## Your job
1. <specific, verifiable action — "run X and confirm Y", not "check things
   look good">
2. ...

## What Claude could NOT verify
<the sandbox has no display/audio/real input — always name what that means
concretely for this handoff, e.g. "deflection math confirmed numerically,
but not confirmed to feel right in actual play">

## If something's broken
Fix it, add a regression test for whatever you find (see SKILLS.md pitfall
notes on testing direction/sign, not just magnitude), commit, push, and
say so plainly in HANDOFF_TO_CLAUDE.md — not "should be fine now."
```

## Format: HANDOFF_TO_CLAUDE.md (Hermes → Claude)

```markdown
# Handoff to Claude — <date>

**Commit:** <short hash> on master
**Tested:** <how — real venv? real display? which mode(s)?>

## Results against Claude's "Your job" list
1. <item> — PASS / FAIL / PARTIAL — <one line of evidence, not just a verdict>
2. ...

## New issues found
<repro steps if a bug, not just "something felt off">

## New files/tests added this session
<list>

## Open questions for Claude
<anything needing a decision or a fix only Claude can reasonably make>

## Environment notes
<only if changed — venv path, pygame version, OS quirks>
```

## Rules for both agents

- **Overwrite, don't append.** Git history is the log. The handoff file is
  a mailbox, not a diary.
- **Verdicts need evidence.** "Tests pass" needs the actual test output or
  count. "Feels right" needs what you actually did to check that.
- **Name what you couldn't verify**, not just what you did. Claude has no
  display/audio; Hermes may be running on a smaller/free-tier model some
  sessions and should say so if it's uncertain about something subtle.
- **Last commit of a session should be the handoff file update.** So the
  other agent's very next `git pull` + read gets the whole picture without
  digging through commit history.
- **Any command meant for Daniel to run himself must be a full copy-paste
  block, always starting with `cd C:\Users\dansl\PONG_GAME`.** He's not
  yet comfortable with manual directory navigation — don't assume the
  shell is already in the right place, and don't split navigation and
  action across separate instructions he has to stitch together. See
  SKILLS.md "CLI Instruction Format" for the exact convention.
