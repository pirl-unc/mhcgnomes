# Project Instructions

See @AGENTS.md for verification steps, workflow principles, and domain knowledge.

---

## Claude Code-Specific

### Plan Mode
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- Use plan mode for verification steps, not just building

### Scientific Claims
- Before editing anything in `mhcgnomes/data/`, read the authority — see
  "Scientific Domain Knowledge" in @AGENTS.md. Use WebFetch/WebSearch on
  IPD-MHC, IMGT/HLA and the primary literature; do not answer from memory.
- Re-read any specific claim verbatim before acting on it. Summarized pages
  routinely invent plausible rows.
- Cite what you find in the YAML or code next to the change, with a PMID or URL.

### Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution
