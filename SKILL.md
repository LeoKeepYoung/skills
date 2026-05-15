---
name: procedural-skills
description: Create, refine, and maintain Codex procedural skills in this repository. Use when the user asks to develop a skill, add or update SKILL.md instructions, organize scripts, references, assets, or agents metadata, validate skill structure, or prepare skill changes for Git.
---

# Procedural Skills

## Development Workflow

1. Clarify the target behavior with concrete user examples before expanding the skill.
2. Keep `SKILL.md` focused on procedural guidance that another Codex instance needs at execution time.
3. Add `scripts/`, `references/`, and `assets/` only when they directly support repeatable skill behavior.
4. Prefer scripts for fragile or repetitive operations that need deterministic execution.
5. Keep reference files one level below the skill root and link them directly from `SKILL.md`.
6. Validate the skill after meaningful edits before committing or publishing.

## Repository Standards

- Treat this repository root as the active skill folder unless the user explicitly asks for a nested skill.
- Keep YAML frontmatter limited to `name` and `description`.
- Use hyphen-case skill names in frontmatter.
- Keep `agents/openai.yaml` aligned with the current skill purpose.
- Avoid extra documentation files unless the user explicitly asks for them.
- Preserve unrelated user changes in the worktree.

## Validation

Run the skill creator validation script after structural or frontmatter changes:

```bash
/Users/luoyu/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/luoyu/Projects/procedural_skills
```

Use the result to fix frontmatter, naming, or required-file issues before moving on.
