# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues in `4238love/yimingqiantu`. Use the `gh` CLI for issue-tracker operations when a skill asks to publish, fetch, label, comment, or close an issue.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc or body file for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, also fetching labels when triage state matters.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`.
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`.
- **Close**: `gh issue close <number> --comment "..."`.

Infer the repo from `git remote -v` — `gh` does this automatically when run inside this clone.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in `4238love/yimingqiantu`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments` from this repo.
