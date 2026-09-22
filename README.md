# Class 07 lab: from a GitHub repository to a published image

Work in pairs and build the activity progressively:

1. **Create a GitHub repository with a working pipeline.**
2. **Make the whole pipeline run only on pushes to `main`.**
3. **Publish the Python app's tested image to the repository's linked GitHub Container Registry package.**

**Deliver:** the repository URL, `.github/workflows/ci.yml`, and `evidence.md` with
your actual run, branch-filter and image-retrieval evidence. Keep the image for Class 08.

**AIAS Level 4:** AI may assist specific tasks. Verify its output, explain your
decisions and declare the tool, task and verification in `evidence.md`, or write
`none`. Use synthetic data; keep credentials out of code, prompts and evidence.
This activity is formative unless a published statement specifies assessment.
Practical work is moderately significant and collectively contributes 10% under
the Academic Guide; this lab sets no individual weight, deadline or submission channel.

## Before starting

- One GitHub account per pair, with permission to create a repository, run GitHub
  Actions and publish a package. Authenticate Git over HTTPS or SSH before class.
- Git, Bash and Python 3.12+. Docker with Linux containers is needed to retrieve
  and run the published image locally; the hosted runner performs the builds.
- Network access to GitHub, GitHub Container Registry (GHCR) and Docker Hub.
- The image targets **linux/amd64**. ARM laptops need configured amd64 emulation
  or a shared compatible machine for the final check. Windows users can use WSL2.

Use an institution-approved account and visibility setting. Standard hosted runners
for public repositories are currently free; private-repository allowances and
package policies are account-dependent. Use the instructor's supported route if
access is blocked; no paid upgrade, GPU or production cloud deployment is required.

### Supplied files

| File | Purpose |
| --- | --- |
| `app.py`, `test_app.py` | Small HTTP scoring service and five source tests. |
| `Dockerfile`, `.dockerignore` | Package only the app using a pinned Python base image. |
| `smoke_test.py` | Check health and three HTTP scoring responses. |
| `ci/verify_image.sh` | Start an image, check it and remove its test container. |
| `ci/publish.sh`, `ci/record_release.py` | Push the existing image and record source/run/digest/platform. |
| `ci.yml.starter` | Runnable Step 1 workflow: source tests on each push. |
| `package-job.yml.starter` | Step 3 job fragment with four marked gaps. |
| `evidence.md` | Record actual observations for the three steps. |

The app uses a deterministic rule and synthetic scores, without a trained model
or third-party Python packages. Its `http.server` implementation is for teaching.

## Step 1 — Create the repository and first pipeline

### Create and clone your repository

1. Sign in to GitHub. Select **+ → New repository**.
2. Choose your personal account or an approved organisation and name the repository
   **`class07-python-app`**. Choose the approved visibility; enable **Add a README**.
3. Click **Create repository**. Ensure the default branch is **`main`**. If it has
   another name, rename that default branch to `main` using GitHub's branch rename
   action before continuing.
4. Open **Code** and copy the HTTPS or SSH clone URL for your chosen authentication
   method. From a local parent folder outside the course materials, run:

```bash
read -r -p 'Paste your repository clone URL: ' REPO_URL
git clone "$REPO_URL" class07-python-app
cd class07-python-app
git branch --show-current
```

The last command must print `main`. Copy **all supplied starter files** into the
root of this new clone, including `.dockerignore` and `.gitignore`. Replace the
newly generated README with this supplied README. Keep the clone's `.git/`
directory; place `app.py`, `Dockerfile` and `ci/` directly at the repository root.

### Add the workflow and push it

All remaining commands run from the root of your new repository.

```bash
mkdir -p .github/workflows
cp ci.yml.starter .github/workflows/ci.yml
python3 -m unittest -v
git status --short
git add .github/workflows/ci.yml app.py test_app.py smoke_test.py Dockerfile \
  .dockerignore .gitignore ci ci.yml.starter package-job.yml.starter README.md evidence.md
git diff --cached
git commit -m "Add first Python CI pipeline"
git push origin main
```

Open **Actions → Class 07 delivery → your new run**. The starter checks out the
source and runs `python3 -m unittest -v` in a job called `test`.

**Checkpoint:** five tests pass with `OK`; the run is successful. Save the repository
URL, run URL, source commit and actual test result in `evidence.md`.

Read the workflow: `on: [push]` currently starts it on push events, without a branch
restriction. No image is published yet. Files ending in `.starter` are teaching
scaffolds; only the `.yml` file inside `.github/workflows/` is active.

## Step 2 — Run only when main receives commits

### Filter the entire workflow

In `.github/workflows/ci.yml`, replace `on: [push]` with:

```yaml
on:
  push:
    branches: [main]
```

Keep the existing `test` job. Do not add `pull_request`, `workflow_dispatch`, a
schedule or tag triggers. A job-level `if` would only skip that job; it would not
stop the workflow run itself from being created.

```bash
git add .github/workflows/ci.yml
git commit -m "Run CI only on main pushes"
git push origin main
```

**Checkpoint:** this push to main creates a passing run. A commit made only on your
laptop does not trigger GitHub Actions: it must reach GitHub through a push. A PR
merge into main also updates main and can trigger this push-based workflow.

### Prove the branch filter

Create the test branch **after the filtered workflow is committed on main**. This
ensures the branch inherits the new trigger rather than the old broad one.

```bash
git switch -c trigger-check
```

Add the sentence `Branch filter check.` at the end of `README.md`, save it, then:

```bash
git add README.md
git commit -m "Check the non-main trigger"
git push -u origin trigger-check
git rev-parse HEAD
```

Inspect the Actions page for that branch and commit. **Expected:** no new
`Class 07 delivery` run for this push. Record the SHA and observation; do not invent
a run URL for an event that did not create a run.

Bring the same commit onto main and push it:

```bash
git switch main
git merge --ff-only trigger-check
git push origin main
```

**Checkpoint:** a passing run now appears for that commit on main. Record its URL.
The contrast is the branch receiving the push, not a difference in application code.
Coordinate with your partner so main is not changed separately during this check.

## Step 3 — Publish the Python app image to GHCR

### Add the package job

Git stores source at `github.com/OWNER/class07-python-app`. Container image content
is stored separately in a **package** at `ghcr.io/owner/class07-python-app` and linked
to that repository. Do not commit an image archive into Git.

Append the contents of `package-job.yml.starter` to `.github/workflows/ci.yml`.
Its `package:` key belongs under the existing `jobs:`, at the same indentation as
`test:`. Do not introduce a second `jobs:` key or replace the main-only trigger.

Keep `needs: test`: the image job must wait for the source tests to succeed. Complete
the fragment's four TODOs:

1. Change the package job's permission from `packages: read` to **`packages: write`**.
   Keep `contents: read` for source checkout.
2. Replace the build placeholder with the build command below.
3. Replace the packaged-check placeholder with the verification command below.
4. Replace the publication placeholder with the publication helper below.

The supplied naming step sets `IMAGE` through `GITHUB_ENV` for later steps. Its
value is `ghcr.io/owner/repository:sha-COMMIT-run-RUN-ATTEMPT`, using real values
from this run and a lowercase repository name. Those capitalised words illustrate
the pattern; they are not identifiers to paste.

### Build and check the same image

Use a multiline `run: |` block for the build:

```bash
source_url="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY"
docker build --platform linux/amd64 --provenance=false \
  --label "org.opencontainers.image.revision=$GITHUB_SHA" \
  --label "org.opencontainers.image.source=$source_url" \
  -t "$IMAGE" .
```

Use this command in the next step:

```bash
bash ci/verify_image.sh "$IMAGE"
```

The helper starts that image, checks `/health` and scores `0.2`, `0.5` and `0.9`,
then removes the test container. Expected acceptance line:

```text
PASS: health + 3 HTTP scoring cases
```

The source label links the package to the GitHub repository; the revision label
records the source commit. Labels are metadata, not signed provenance. This lab
selects a single amd64 image and disables extra provenance output to keep the
introductory handover simple. A tag containing a commit is still a mutable tag.

### Authenticate, publish and inspect the package

Authentication is already supplied in the fragment. GitHub generates the job's
`GITHUB_TOKEN`, and `packages: write` authorises publication subject to repository
and organisation policy. The login step passes the token through standard input.
You do **not** need to create or store a personal publish token.

Replace the final publication placeholder with:

```bash
bash ci/publish.sh "$IMAGE"
```

This pushes the existing tested image and writes its full repository digest,
source, run/attempt and platform into the package job summary. Keep it after the
packaged check; do not add another build or failure override. `always()` is used
only for logout in the supplied fragment.

```bash
git add .github/workflows/ci.yml
git diff --cached
git commit -m "Publish the tested Python image to GHCR"
git push origin main
```

**Checkpoint:** `test` passes, then `package` builds, verifies and publishes. Open
the repository's **Packages** link, or your account's **Packages** tab, and find
`class07-python-app`. Verify the linked source repository and the version created
by this run. Save the package URL and the package job summary in `evidence.md`.

### Retrieve and run the published image

GHCR packages are **private on first publication**, even when their source repository
is public. For this synthetic lab image, set it public in **Package settings →
Change visibility** if the class policy permits. Otherwise authenticate locally
with an authorised personal access token **(classic)** containing `read:packages`
and any required organisation SSO authorisation:

```bash
read -r -p 'GitHub username: ' GH_USER
read -r -s -p 'Read-only package token: ' CR_PAT
printf '\n'
printf '%s' "$CR_PAT" | docker login ghcr.io -u "$GH_USER" --password-stdin
unset CR_PAT
```

Docker can retain credentials in its configured credential store. The generated
workflow token is for the hosted job; do not copy it to your laptop.

Copy the **complete reference after `image=`** from the package job summary. It must
contain the repository and `@sha256:` followed by 64 hexadecimal digits, not dots,
a local image ID or just a tag. In your local repository root:

```bash
docker version
read -r -p 'Paste the complete image= value: ' REF
docker pull --platform linux/amd64 "$REF"
bash ci/verify_image.sh "$REF"
```

**Final checkpoint:** pull succeeds and the retrieved image reports
`PASS: health + 3 HTTP scoring cases`. Save actual output, the full digest and
`linux/amd64`. Do not rebuild for this check. The helper removes its test container.

Complete `evidence.md` and retain the image for Class 08. A private image will need
an appropriate cluster pull credential; the instructor will confirm that setup.
Log out after using a local credential when finished:

```bash
docker logout ghcr.io
```

## Optional continuation — prove a failed check blocks publication

In this disposable repository, change `value >= 0.5` to `value > 0.5` in `app.py`,
leave the tests unchanged, and commit/push to main. Expect `test_exact_boundary`
to fail and `package` to be skipped. Record that run, restore `>=`, commit/push the
repair and recover the new image by digest. The previous good package can still
exist; its presence does not mean the failed candidate was published.

Alternatively, add a useful test or adapt the same pipeline to your project.
Optional continuation can be completed independently without an attendance penalty.

## Troubleshooting

| Observation | Check |
| --- | --- |
| Git clone/push authentication fails | Use your configured SSH key or authorised HTTPS Git credential; a GitHub account password is not an HTTPS Git token. |
| No first workflow run | Exact root path `.github/workflows/ci.yml`; committed/pushed workflow; Actions permitted; no YAML error. |
| Feature push still starts a run | The branch contains Step 2's filtered workflow, not the older starter; check other workflow files too. |
| PR opening starts this workflow | Remove the `pull_request` event; the final trigger is only push with `branches: [main]`. |
| Image job starts despite failed source tests | Check `needs: test` and remove failure overrides. |
| Registry push denied | Package job has `packages: write`; institution permits publication; repository has access to any existing package with the same name. |
| Package missing from repository sidebar | Check account Packages and the `org.opencontainers.image.source` label/repository connection. |
| Private pull denied | Package visibility and authorised read credential; source visibility is separate. |
| HTTP failure or `exec format error` | Read container logs; verify Docker is running and amd64 execution/emulation is supported. |

## If hosted access is unavailable

Pair on a working GitHub account where possible. The instructor's local-registry
fallback can demonstrate the image stages, but it cannot create a GitHub repository
or verify GitHub triggers and GHCR permissions. Mark incomplete hosted checks as
pending and label local observations **local simulation**; do not invent run URLs.

## Primary references

- [Create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Docker image pull](https://docs.docker.com/reference/cli/docker/image/pull/)

Technical choices checked 22 September 2026. The supplied action is pinned to the
full commit resolved from `actions/checkout` v6 on that date. Account policies and
permissions still require classroom preflight.
Branch filter check.
