# Project Instructions

See @AGENTS.md for verification steps, workflow principles, and domain knowledge.

---

## Claude Code-Specific

### Plan Mode
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- Use plan mode for verification steps, not just building

### Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution
