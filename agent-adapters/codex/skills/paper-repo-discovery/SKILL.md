---
name: paper-repo-discovery
description: Find and clone the official or most credible public code repository for a specific research paper. Use when Codex is given a paper title, arXiv URL or ID, DOI, OpenReview page, publisher page, project page, PDF URL, or local paper file and needs to identify candidate code repositories, verify officialness or credibility, ask for confirmation when ambiguous, clone the selected repository locally, and write a resolution report. This skill covers repository discovery and cloning only; environment setup, resource acquisition, evaluation, and optimization belong to later runnable/onboard skills.
---

# Paper Repo Discovery

Use this skill to turn one paper input into one cloned local code repository, when a credible repository exists.

The agent does the work directly. Do not implement a separate program or pipeline for the discovery logic. Use live web lookup whenever the paper identity, code URL, repository status, or latest public metadata matters.

## Workflow

1. Normalize the paper input.
   - Accept titles, arXiv IDs or URLs, DOI links, OpenReview pages, publisher pages, project pages, PDF URLs, and local PDF paths.
   - Extract or verify title, authors, year, venue, arXiv ID, DOI, method acronym, project page, and any stated code URL.
   - If the input is too ambiguous to identify one paper after lookup, ask the user to clarify before repository search.

2. Search the paper source first.
   - Inspect the abstract page, PDF landing page, OpenReview metadata, arXiv comments, author notes, project page links, supplementary material, appendix, footnotes, and code/artifact sections.
   - Search within available paper text for: `code`, `github`, `implementation`, `artifact`, `repository`, `project page`, `supplementary`, `available at`, and `released`.
   - Treat a repository linked from the paper page, author page, project page, or paper PDF as the strongest candidate, but still verify it.

3. Search external sources when no strong code URL is found.
   - Use web search queries such as:
     - `"<exact paper title>" GitHub`
     - `"<exact paper title>" code`
     - `"<arXiv ID>" GitHub`
     - `"<method acronym>" "<first author last name>" GitHub`
     - `site:github.com "<exact paper title>"`
     - `site:github.com "<arXiv ID>"`
   - Check Papers with Code, author homepages, lab pages, conference artifact pages, Hugging Face pages, and organization/project pages when relevant.
   - Prefer primary or semi-primary sources over SEO mirrors, blog summaries, package indexes, and random forks.

4. Score candidates by evidence.
   - High confidence: paper, arXiv/OpenReview page, official project page, or author/lab page directly links the repo, and the repo README/citation links back to the paper, title, arXiv ID, DOI, or authors.
   - Medium confidence: repo README strongly matches the title/method/authors and timing, but the link is indirect or multiple plausible candidates exist.
   - Low confidence: repo only matches keywords, is a fork, is a third-party reproduction, or lacks paper-identifying evidence.
   - Penalize candidates that are forks without original provenance, unrelated homonyms, tutorial ports, incomplete copies, stale mirrors, or repositories with mismatched authors/title/year.

5. Decide whether to clone.
   - If exactly one high-confidence official repository exists, present the evidence and clone it unless the user asked to review before clone.
   - If confidence is medium, low, or there are multiple plausible repositories, ask the user to choose or approve before cloning.
   - If no official repository is found, say so clearly. Offer credible unofficial implementations separately, but do not clone one by default.

6. Clone safely.
   - Clone into a user-approved or task-appropriate local repository root. Prefer a dedicated paper repository directory when one exists in the workspace context.
   - Before cloning, report the selected URL, confidence, key evidence, and target directory.
   - If the destination already exists, inspect it and avoid overwriting. Reuse it only when its git remote matches the selected repository, otherwise ask the user.
   - After cloning, verify `git remote -v`, current branch, recent commit, README/citation evidence, and the final local path.

7. Write a resolution report.
   - Create or update `paper_repo_resolution.md` in the task run directory or the cloned repository parent when a task run directory is not established.
   - Include the original paper input, normalized paper identity, search sources, candidate table, selected repo URL, confidence, evidence, clone path, verification checks, and unresolved concerns.

## Candidate Report Shape

Use this shape in the final answer and in `paper_repo_resolution.md`:

```markdown
# Paper Repo Resolution

## Paper
- Input:
- Title:
- Authors:
- Year/Venue:
- arXiv/DOI:

## Candidates
| Rank | URL | Confidence | Officialness | Evidence | Concerns |
|---|---|---|---|---|---|

## Decision
- Selected URL:
- Decision:
- Clone path:
- Reason:

## Verification
- Remote:
- Branch:
- README/citation match:
- Notes:
```

## Boundaries

Do:

- use live lookup for paper metadata and repository discovery
- distinguish official, likely official, and unofficial repositories
- cite or summarize concrete evidence before cloning
- ask for confirmation when ambiguous
- record enough provenance for another agent to audit the choice

Do not:

- implement repository discovery as a new Python or TypeScript pipeline
- assume the first GitHub result is official
- clone a third-party reproduction without user approval
- overwrite or delete an existing local repository
- install dependencies, download datasets/models, run evaluation, or modify cloned code
- continue into environment setup; hand off to a later runnable/onboard skill
