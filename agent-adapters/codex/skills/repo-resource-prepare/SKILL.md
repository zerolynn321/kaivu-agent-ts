---
name: repo-resource-prepare
description: Identify, acquire, and stage all required runtime resources for an onboarded research repository into a run-local resource directory. Use after repo-onboard has produced or reused config.yaml, or whenever Codex acting as AgentInit must inspect a repository for required datasets, pretrained models, checkpoints, caches, local path assumptions, API tokens, and external URLs; download or copy required resources into the run directory; optionally bind repository paths to staged resources; and write resource_manifest.yaml plus resource_acquisition_report.md. This skill does not install dependencies, create environments, run baseline evaluations, or modify experiment logic.
---

# Repo Resource Prepare

Use this skill when AgentInit receives an onboarded repository and must make required resources available under the run directory before environment setup or baseline execution.

The agent does the work directly. Do not implement a separate Python or TypeScript pipeline for resource discovery or acquisition.

## Agent Contract

Role: `AgentInit`

Inputs:

- cloned repository path
- repository-local `config.yaml`
- run directory or resource root where required resources must be staged
- optional `onboard_report.md`
- optional user approval for large downloads, credentials, or path binding

Required outputs:

- `<run_dir>/resources/` containing every acquired required resource
- `<run_dir>/resource_manifest.yaml`
- `<run_dir>/resource_acquisition_report.md`

Optional outputs:

- repository symlinks or path notes only when needed for the configured command to read staged resources

Handoff:

- After required resources are staged or blockers are documented, hand off to the environment setup skill.
- Do not continue into package installation, environment creation, baseline execution, optimization, or code changes.

## Workflow

1. Confirm context.
   - Resolve the repository path and run directory.
   - Read `<repo>/config.yaml` before scanning.
   - Read `<repo>/onboard_report.md` and nearby `paper_repo_resolution.md` when present.
   - Create `<run_dir>/resources/` if resources must be staged and the path is inside the user-approved workspace/run root.

2. Discover resource requirements.
   - Inspect README files, docs, examples, scripts, notebooks, configs, CLI guides, evaluation commands, dataset loaders, model loaders, checkpoint paths, and hard-coded local paths.
   - Search for terms such as `data`, `dataset`, `datasets`, `download`, `pretrained`, `pre-trained`, `checkpoint`, `ckpt`, `weights`, `model`, `cache`, `embedding`, `corpus`, `index`, `tokenizer`, `huggingface`, `drive.google`, `dropbox`, `zenodo`, `kaggle`, `wget`, `curl`, and `gdown`.
   - Classify resources as `dataset`, `model`, `checkpoint`, or `misc`.
   - Mark each resource as `required: true` only when the configured eval/smoke/baseline command or documented minimal run path needs it.
   - Treat optional full-paper datasets, giant pretrained weights, or alternative benchmark resources as optional unless the selected command requires them.

3. Build the resource manifest before downloading.
   - For each resource, record `name`, `type`, `source_url`, `local_path`, `acquired_path`, `expected_size_bytes` if known, `required`, `status`, and `notes`.
   - Use paths as seen from the repository root for `local_path`.
   - Put unresolved credentials, inaccessible URLs, license gates, manual forms, or ambiguous resources in `unresolved_requirements`.
   - Present the plan before downloading large files, credentialed resources, or resources from untrusted/non-primary sources.

4. Acquire required resources.
   - Required resources must end up under `<run_dir>/resources/` or be explicitly marked blocked with a reason.
   - If a required resource already exists in the repository, copy it into `<run_dir>/resources/` and record the copy.
   - If it already exists in the run resource directory, reuse it.
   - If a required resource has a direct URL, download it into `<run_dir>/resources/`.
   - If a required resource requires manual access, authentication, license acceptance, or unclear source selection, stop and ask the user.
   - Do not silently skip required resources.

5. Bind repository paths when needed.
   - If the configured command expects a repo-relative path and the resource was staged elsewhere, either create a symlink from the expected repo path to the staged resource or record an explicit path-binding instruction.
   - Ask before replacing an existing regular file or directory.
   - Never delete or overwrite repository resources without user approval.
   - Keep backups under a clearly named backup directory if the user approves replacement.

6. Write reports.
   - Write `<run_dir>/resource_manifest.yaml`.
   - Write `<run_dir>/resource_acquisition_report.md`.
   - Include sources, staged paths, copied/downloaded/reused/blocked status, binding actions, unresolved requirements, and next handoff state.

7. Verify.
   - Re-read the manifest and report.
   - Confirm every `required: true` resource is either `available` with an existing `acquired_path`, or `blocked` with a concrete next action.
   - Do not run the full baseline. Cheap file existence checks, checksums, archive listings, and directory listings are allowed.

## Manifest Shape

Use this shape for `resource_manifest.yaml`:

```yaml
repo_path: ""
run_dir: ""
resource_root: ""
resources:
  - name: ""
    type: "dataset" # dataset | model | checkpoint | misc
    source_url: ""
    local_path: ""
    acquired_path: ""
    expected_size_bytes:
    required: true
    status: "discovered" # discovered | available | missing | blocked | failed
    notes: ""
unresolved_requirements: []
repo_assumptions: []
notes: ""
```

Use this shape for each item in `resource_acquisition_report.md`:

```markdown
| Resource | Required | Action | Status | Source | Staged path | Repo binding | Notes |
|---|---:|---|---|---|---|---|---|
```

## Decision Rules

- `available`: resource exists under `<run_dir>/resources/` and any required repo path binding is done or documented.
- `missing`: resource is required but no local copy or direct source was found.
- `blocked`: resource requires user action, credentials, license acceptance, huge download approval, or source disambiguation.
- `failed`: attempted copy/download failed; include the command or URL and the error summary.
- Optional resources may remain `discovered` or `missing` without blocking the handoff.

## Boundaries

Do:

- stage every required resource into the run directory
- prefer repository, paper, project page, README, and official data links over third-party mirrors
- preserve provenance for every copied or downloaded file
- ask before large downloads, credentialed sources, untrusted mirrors, or path replacement
- keep the process auditable with manifest and acquisition report files

Do not:

- implement resource preparation as a new Python or TypeScript pipeline
- install dependencies, create conda/venv environments, or run package managers
- run full training, long evaluation, or optimization
- change dataset contents, labels, splits, metrics, or evaluation logic
- overwrite existing repository files or directories without explicit user approval
