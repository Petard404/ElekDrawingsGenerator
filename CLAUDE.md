# huiselek – way of working

What we are building and in what order is in docs/handoff-plan.md.
This file is about how we work together.

## Before coding
- Start each milestone with a short plan: what will be built, which
  files will be touched, and how it will be proven to work. Wait for
  my go before any code is written.
- Ask, don't assume. If the plan or my request leaves a real choice
  open, ask. If you proceed on an assumption anyway, state it.
- Stay inside the milestone. No extra features, no refactoring of
  code that works, no new dependencies without asking.

## While coding
- One milestone at a time. Stop when it is done and wait for review.
- If you hit a blocker or the plan turns out to be wrong, stop and
  say so. Do not work around it quietly.

## After coding
- Prove it works. Run the tests and the tool itself, and show me the
  result: test output and the generated PDF. Never report something
  as done that you have not run.
- Explain what changed and why in a few lines. I read and write
  Python, so be brief and technical. No tutorials.
- Say what is not done, not tested, or uncertain.
- Commit once per approved milestone, on main.

## Models and agents
- The main session runs on Opus and acts as orchestrator: plan,
  decide, brief, review, keep the overview. It does not write the
  bulk of the code itself.
- Coding is delegated to Sonnet by default.
- Choose the model per subtask. Sonnet is the default. Go down to
  Haiku for mechanical work (one symbol, repetitive edits,
  docstrings). Go up to Opus only for a design question or a problem
  Sonnet has failed at twice.
- Exception: the main session may make small edits itself when
  delegating would cost more than the change, such as a fix of a few
  lines after review. Anything larger is delegated.
- Every brief states: goal, files to read, exact output, and how it
  will be checked. If you cannot write that in a few lines, the task
  is not ready to delegate; split it or plan it further.
- Verify every delegated result yourself: run it, render it, test
  it. A subagent's own report is not proof.
- At the end of each milestone, have one agent that has not seen the
  work review it against the milestone goal.
- Delegate one task at a time, not in parallel.
- Never have two agents edit the same files at once.
- Tell me what was delegated, to which model, and what came back,
  including findings you chose not to act on.

## Token use
- I am on a Pro subscription with usage limits shared across all my
  Claude use. Treat tokens as a limited budget.
- One milestone per session. At the end, update docs/progress.md
  with the current state and the next step, so the next session
  starts fresh instead of carrying the whole history.
- Read only what the task needs. Search for the relevant part rather
  than opening whole files, and do not re-read unchanged files.
- Never print generated SVG or whole files into the conversation.
  Show paths, diffs and short summaries. To check a drawing, render
  one page and look at it.
- Run tests quietly: show failures and the summary line only.
- Read the reference drawings once. Record what you need from them
  in docs/symbol-notes.md and work from the notes afterwards.
- When tuning layout, change one thing, render one page, check.
  Do not regenerate everything on each attempt.
- If a task looks expensive for what it delivers, say so before
  starting and propose a cheaper route.
- If we hit usage limits, say so and suggest which remaining work
  could move to a smaller model.

## Decision log
- Keep docs/decisions.md. One entry per decision: date, the decision,
  the alternatives considered, the reason.
- Log a decision when we choose a library, change the input format,
  change a layout rule, or depart from the plan.
- Check the log before proposing something we already decided
  against.

## Disagreement
- Be direct. If my instruction is a bad idea, or conflicts with the
  plan or an earlier decision, say so and say why before doing it.
- If I still want it, do it and log it.

## Conventions
- Code, comments, docs and commit messages in English. All text on
  the drawing in Dutch.
- The tool runs on Windows. Dependencies must install with pip
  alone, with no separately installed native libraries.
