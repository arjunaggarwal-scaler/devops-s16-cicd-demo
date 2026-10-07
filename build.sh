#!/usr/bin/env bash
# Build script (extended from the class 10-final-cicd-pipeline/build.sh).
# Produces a versioned, deployable source bundle in dist/ plus build metadata.
set -euo pipefail

APP_NAME="s16-calculator-api"
VERSION=$(python3 -c "import app; print(app.__version__)")
GIT_SHA="${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo local)}"
SHORT_SHA="${GIT_SHA:0:7}"

echo "================================="
echo "Starting Application Build"
echo "================================="
rm -rf build dist
mkdir -p build dist

cp -r app requirements.txt Dockerfile build/
find build -name '__pycache__' -type d -prune -exec rm -rf {} +

cat > build/build-info.txt <<INFO
Application: ${APP_NAME}
Version:     ${VERSION}
Git SHA:     ${GIT_SHA}
Built by:    ${GITHUB_ACTOR:-$(whoami)}
Run:         ${GITHUB_RUN_ID:-local} (attempt ${GITHUB_RUN_ATTEMPT:-1})
Python:      $(python3 --version 2>&1)
Build Date:  $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Build Status: SUCCESS
INFO

tar -czf "dist/${APP_NAME}-${VERSION}-${SHORT_SHA}.tar.gz" -C build .
( cd dist && sha256sum ./*.tar.gz > SHA256SUMS 2>/dev/null || shasum -a 256 ./*.tar.gz > SHA256SUMS )

echo ""
echo "Build files:"
ls -la build dist
echo ""
cat build/build-info.txt
echo ""
echo "Build completed successfully."
