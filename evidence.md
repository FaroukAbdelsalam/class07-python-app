# Class 07: repository, trigger and image evidence

Use actual output. Replace each blank; do not copy the acceptance text as a result.

## Step 1 — Create the repository and pipeline
- Repository URL:
- Workflow path:
- First passing run URL and source commit:
- Actual unit-test result:

## Step 2 — Run only on pushes to main
- Commit/run that installed the main-only trigger:
- `trigger-check` branch commit SHA:
- What the Actions page showed for that branch/SHA:
- Run URL after the same commit was pushed to `main`:
- Explain why a local commit alone does not start GitHub Actions:

## Step 3 — Publish and retrieve the Python image
- Package page URL (GHCR, linked to this repository):
- Source commit, run URL and attempt:
- Actual source-test and packaged HTTP test results:
- Complete registry reference (`repository@sha256:` plus 64 hexadecimal digits):
- Platform:
- Exact pull command:
- Actual pulled-image HTTP test output:

## Limits and explanation
- One thing these tests do not establish:
- Explain the difference between the Git repository and its linked image package:
- AI assistance used (tool, task, verification), or `none`:

## Optional failure-and-repair extension
- Failed commit/run, useful assertion and skipped package job:
- Repaired commit/run and recovered digest:

Save the successful package job summary, or paste its release record above.
If using a fallback, explicitly mark the uncompleted hosted checks and local
simulation results. Do not invent a repository, run URL or successful GHCR push.
