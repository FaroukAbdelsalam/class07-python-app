# Class 07: repository, trigger and image evidence

**Name:** Farouk Abdelsalam
**Date:** 22/09/2026
**Machine:** MacBook Air (Apple chip), Docker Desktop 4.41.2
**Folder:** ~/class07/class07-python-app
**Repository:** https://github.com/FaroukAbdelsalam/class07-python-app

## Step 1: Create the repository and pipeline

- Repository URL: https://github.com/FaroukAbdelsalam/class07-python-app
- Workflow path: .github/workflows/ci.yml
- First passing run URL and source commit: run #1, https://github.com/FaroukAbdelsalam/class07-python-app/actions/runs/35758078424, commit 025baf30376caff4eee9e9cf45191a15a6d0def4
- Actual unit-test result: 5 tests ran, result OK (output below)

Commands:

```bash
mkdir -p .github/workflows
cp ci.yml.starter .github/workflows/ci.yml
git add .github/workflows/ci.yml app.py test_app.py \
  smoke_test.py Dockerfile .dockerignore .gitignore \
  ci *.starter README.md evidence.md
git commit -m "Add first Python CI pipeline"
git push origin main
```

Output of the "Source contract" step in run #1:

```
test_above_boundary (test_app.ClassifyTests.test_above_boundary) ... ok
test_below_boundary (test_app.ClassifyTests.test_below_boundary) ... ok
test_endpoints (test_app.ClassifyTests.test_endpoints) ... ok
test_exact_boundary (test_app.ClassifyTests.test_exact_boundary) ... ok
test_invalid_values (test_app.ClassifyTests.test_invalid_values) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```

Acceptance check: the test job reports five passing tests and OK. It passes.

## Step 2: Run only on pushes to main

- Commit/run that installed the main-only trigger: commit 7de7d4fd3fbc2012ef0da1da92ef7e613a233671, run #2, https://github.com/FaroukAbdelsalam/class07-python-app/actions/runs/35758775876
- `trigger-check` branch commit SHA: 52c35e0df1918069b13cf86adb87ea61cfe3ecce
- What the Actions page showed for that branch/SHA: no run. After pushing trigger-check, the Actions page still had no run for that branch. At the end of the lab it lists 4 runs and all 4 are on main.
- Run URL after the same commit was pushed to `main`: run #3, https://github.com/FaroukAbdelsalam/class07-python-app/actions/runs/35759315071 (commit 52c35e0df1918069b13cf86adb87ea61cfe3ecce, passed)
- Explain why a local commit alone does not start GitHub Actions: GitHub Actions starts a run when an event happens on GitHub. git commit only changes the repository on my laptop, so GitHub does not know about it. The event only happens when git push updates the branch on GitHub. Our trigger also only accepts push events to main, so the push to trigger-check did not start a run either.

The trigger now is:

```yaml
on:
  push:
    branches: [main]
```

Commands:

```bash
git switch -c trigger-check
# added "Branch filter check." at the end of README.md
git add README.md
git commit -m "Check the non-main trigger"
git push -u origin trigger-check
git switch main
git merge --ff-only trigger-check
git push origin main
```

The branch was created after commit 7de7d4f, so it already had the filtered workflow and not the old on: [push]. The same commit 52c35e0 created no run when pushed to trigger-check and one passing run when pushed to main. The only difference was the branch that received the push.

Acceptance check: branch commit with no run, and a passing run after the same commit reached main. It passes.

## Step 3: Publish and retrieve the Python image

- Package page URL (GHCR, linked to this repository): https://github.com/users/FaroukAbdelsalam/packages/container/package/class07-python-app
- Source commit, run URL and attempt: b9dec0a4d9053fe80fd7d0b32029f484769aabb2, https://github.com/FaroukAbdelsalam/class07-python-app/actions/runs/35759642767, attempt 1
- Actual source-test and packaged HTTP test results: the test job passed first, then the package job (needs: test) printed `PASS: health + 3 HTTP scoring cases` before the push
- Complete registry reference: ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874
- Platform: linux/amd64
- Exact pull command: `docker pull --platform linux/amd64 ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874`
- Actual pulled-image HTTP test output: `PASS: health + 3 HTTP scoring cases` (full output below)

In the package job I completed the four TODOs: packages: write, one build with the platform, revision and source labels, bash ci/verify_image.sh "$IMAGE", and bash ci/publish.sh "$IMAGE". The order is build, test the image, log in, push. There is no second build.

"Test the packaged application" step in run #4:

```
PASS: health + 3 HTTP scoring cases
172.17.0.1 - - [22/Sep/2026 17:17:14] "GET /health HTTP/1.1" 200 -
172.17.0.1 - - [22/Sep/2026 17:17:14] "GET /score?value=0.2 HTTP/1.1" 200 -
172.17.0.1 - - [22/Sep/2026 17:17:14] "GET /score?value=0.5 HTTP/1.1" 200 -
172.17.0.1 - - [22/Sep/2026 17:17:14] "GET /score?value=0.9 HTTP/1.1" 200 -
```

Release record from the package job (run #4):

```
sha-b9dec0a4d9053fe80fd7d0b32029f484769aabb2-run-35759642767-1: digest: sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874 size: 1572
source=b9dec0a4d9053fe80fd7d0b32029f484769aabb2
run=https://github.com/FaroukAbdelsalam/class07-python-app/actions/runs/35759642767
attempt=1
checks=source unit tests + packaged HTTP smoke test passed before publish
image=ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874
platform=linux/amd64
```

The package was private after the first push. I changed it to public in Package settings before pulling, which is allowed because the data is synthetic.

Pull and check on my Mac (no rebuild, the image comes from GHCR):

```bash
cd ~/class07/class07-python-app
REF="ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874"
docker pull --platform linux/amd64 "$REF"
bash ci/verify_image.sh "$REF"
```

Output:

```
ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874: Pulling from faroukabdelsalam/class07-python-app
60163b6ef1dc: Pull complete
1560cfed01dc: Pull complete
80f89b8b86b5: Pull complete
56235e424563: Pull complete
2e19782d7109: Pull complete
dbd0b7849e6c: Pull complete
Digest: sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874
Status: Downloaded newer image for ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874
ghcr.io/faroukabdelsalam/class07-python-app@sha256:819ec17174e546a0185c3491a46ee3ee8304b295471305aed52ff7ccd03ec874
PASS: health + 3 HTTP scoring cases
172.17.0.1 - - [22/Sep/2026 17:31:34] "GET /health HTTP/1.1" 200 -
172.17.0.1 - - [22/Sep/2026 17:31:34] "GET /score?value=0.2 HTTP/1.1" 200 -
172.17.0.1 - - [22/Sep/2026 17:31:34] "GET /score?value=0.5 HTTP/1.1" 200 -
172.17.0.1 - - [22/Sep/2026 17:31:34] "GET /score?value=0.9 HTTP/1.1" 200 -
```

The digest printed by docker pull is the same as the one in the release record, so this is the same image that was tested in run #4. My Docker engine is linux/arm64, so Docker Desktop ran the linux/amd64 image with emulation.

Acceptance check: the pull succeeds and the pulled image reports PASS: health + 3 HTTP scoring cases. It passes.

## Limits and explanation

- One thing these tests do not establish: that the service is ready for production. They only check /health and three score values on one run. There is no check for load, security, or invalid requests over HTTP, and the app uses http.server, which is only for teaching. The labels are also not signed provenance.
- Explain the difference between the Git repository and its linked image package: the Git repository stores the source (app.py, tests, Dockerfile, workflow) and is identified by commits. The package in GHCR stores the built image and is identified by its digest and platform. They are linked by the org.opencontainers.image.source label, but they are separate things with separate visibility: the package was private even though I could see the repository.
- AI assistance used (tool, task, verification), or `none`: I used Claude to explain the steps, help complete the TODOs in the package job and help write this record. I ran every command myself, checked the results in GitHub Actions and in my terminal, compared them with the acceptance checks, and can explain what each step of the workflow does. Only the synthetic data in app.py was used.

## Optional failure-and-repair extension

- Failed commit/run, useful assertion and skipped package job: not done.
- Repaired commit/run and recovered digest: not done.
