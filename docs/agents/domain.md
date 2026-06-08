# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Layout

This is a **single-context** repo.

When present, use:

- `CONTEXT.md` at the repo root for domain vocabulary, core concepts, and project-specific language.
- `docs/adr/` for architectural decision records that affect the area being changed.

If these files or directories do not exist yet, proceed silently. Do not require creating them before doing normal engineering work; producer/documentation skills can add them later when domain terms or architecture decisions need to be captured.

## Before exploring, read these

- `CONTEXT.md` at the repo root, if present.
- Relevant ADRs under `docs/adr/`, if present.

## Use the glossary's vocabulary

When output names a domain concept, such as an issue title, refactor proposal, hypothesis, or test name, use the term as defined in `CONTEXT.md`. Do not drift to synonyms the glossary explicitly avoids.

If the concept needed is not in the glossary yet, either reconsider whether the project already has another term for it or note the gap for future domain-documentation work.

## Flag ADR conflicts

If output contradicts an existing ADR, surface it explicitly rather than silently overriding it, for example:

> Contradicts ADR-0007 — but worth reopening because...
