# devops-s16-cicd-demo

[![CI](https://github.com/arjunaggarwal-scaler/devops-s16-cicd-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/arjunaggarwal-scaler/devops-s16-cicd-demo/actions/workflows/ci.yml)
[![CD](https://github.com/arjunaggarwal-scaler/devops-s16-cicd-demo/actions/workflows/cd.yml/badge.svg)](https://github.com/arjunaggarwal-scaler/devops-s16-cicd-demo/actions/workflows/cd.yml)

Session 16 (CI/CD & GitHub Actions) demo project by **Arjun Aggarwal (24BCS10109)**.

The class `10-final-cicd-pipeline` calculator, extended into a small **Flask web API** with unit tests,
a **Dockerfile**, a **CI workflow** (lint, matrix tests, coverage, build, artifacts, container smoke test
using a repository secret) and a **CD workflow** (push image to GHCR, deploy to a Kubernetes kind cluster
created on the runner, smoke test the Service).

```text
 git push / PR ──► CI (.github/workflows/ci.yml)
                   lint ─┐
                         ├─► test (5 runners: py3.12/3.13/3.14 ubuntu, py3.13 windows, py3.13 macos)
          security-check ┘        │ artifacts: junit.xml + coverage.xml + htmlcov
                                  ▼
                                build  ─► artifacts: calculator-build (bundle), docker-image (tar)
                                  ▼
                          integration-test (downloads docker-image, runs it with secrets.DEMO_API_KEY)

 CI success on main ─► CD (.github/workflows/cd.yml)   [workflow_run, or manual workflow_dispatch]
                        publish: docker build + push ghcr.io/arjunaggarwal-scaler/devops-s16-cicd-demo:sha-<sha>, :latest
                          ▼
                        deploy: kind cluster on runner ─► kubectl apply k8s/ ─► rollout status ─► curl smoke test
```

## Layout

| Path | What it is |
|---|---|
| `app/calculator.py` | Pure calculator functions (add, subtract, multiply, divide, power) |
| `app/main.py` | Flask API: `/`, `/health`, `/api/<op>?a=&b=`, `/api/secure/ping` (needs `X-API-Key`) |
| `tests/` | pytest unit tests for the logic and the HTTP API (coverage gate 90%) |
| `Dockerfile` | `python:3.13-slim`, non-root user, gunicorn, HEALTHCHECK |
| `build.sh` | Creates `build/build-info.txt` and a versioned tarball in `dist/` |
| `k8s/` | Deployment (2 replicas, probes, pull secret, API key from a Secret) and ClusterIP Service |
| `.github/workflows/ci.yml` | CI pipeline |
| `.github/workflows/cd.yml` | CD pipeline |

## Run locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
flake8 . && pytest --cov=app
./build.sh

docker build -t s16-calculator-api:local .
docker run -d --name s16-calc -p 21600:8000 -e API_KEY=demo s16-calculator-api:local
curl "http://localhost:21600/api/add?a=2&b=3"
curl -H "X-API-Key: demo" http://localhost:21600/api/secure/ping
```

Pull the published image:

```bash
docker pull ghcr.io/arjunaggarwal-scaler/devops-s16-cicd-demo:latest
```

## Secrets

The workflows need one repository secret, `DEMO_API_KEY` (a harmless demo value, not a real credential):

```bash
gh secret set DEMO_API_KEY --body "<any demo value>"
```

`GITHUB_TOKEN` is provided automatically; `cd.yml` grants it `packages: write` to push to GHCR.

## Make targets

A `Makefile` wraps the same commands the CI pipeline runs, so you can reproduce each stage locally:

```bash
make install   # install dev dependencies
make lint      # flake8 (same as the CI "lint" job)
make test      # pytest + coverage (90% gate, same as CI)
make build     # versioned source bundle in dist/
make run       # build the image and run it on http://localhost:21600/
make stop      # remove the local container
```
