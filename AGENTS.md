## Before Completing Any Task

Before considering any code change complete, you MUST:

1. **Run `./format.sh`** - Auto-format all code
2. **Run `./lint.sh`** - Verify linting passes (this runs both `ruff check` and `ruff format --check`)
3. **Run `./test.sh`** - Verify all tests pass

Do not tell the user you are "done" or that changes are "complete" until all three of these pass.

## Scripts

- `./format.sh` - Formats code with ruff (run this first)
- `./lint.sh` - Checks linting and formatting (must pass)
- `./test.sh` - Runs pytest with coverage (must pass)
- `./deploy.sh` - Deploys to PyPI (gates on lint.sh and test.sh)
- `./develop.sh` - Installs package in development mode

## Code Style

- Use ruff for formatting and linting
- Configuration is in `pyproject.toml` under `[tool.ruff]`
- Line length: 100 characters
- Target Python version: 3.9+

---

## Workflow Orchestration

### 1. Upfront Planning
- For ANY non-trivial task (3+ steps or architectural decisions): write a detailed spec before touching code
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use planning/verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 3. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between the latest code and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 4. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 5. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Fix failing unit tests without being told how

---

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

---

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Scientific Domain Knowledge
- **Read the literature**: if some code involves scientific or biological concepts, feel free to search for review papers and read those before changing code that expresses scientific concepts.
- **Flag inconsistencies**: if code expresses a scientific model that's at odds with your understanding, note that inconsistency and ask for clarification.
