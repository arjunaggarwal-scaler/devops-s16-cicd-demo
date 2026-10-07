# Convenience targets for local development (mirrors what the CI pipeline runs).
IMAGE ?= s16-calculator-api
PORT  ?= 21600

.PHONY: install lint test build docker run stop clean

install:        ## Install dev dependencies into the active venv
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

lint:           ## Run flake8 exactly as the CI "lint" job does
	flake8 . --count --show-source --statistics

test:           ## Run the unit tests with coverage (90% gate, same as CI)
	pytest --cov=app --cov-report=term-missing --cov-fail-under=90

build:          ## Produce the versioned source bundle in dist/
	./build.sh

docker:         ## Build the container image locally
	docker build --build-arg GIT_SHA=local -t $(IMAGE):local .

run: docker     ## Run the container and expose it on $(PORT)
	docker rm -f s16-calc 2>/dev/null || true
	docker run -d --name s16-calc -p $(PORT):8000 -e API_KEY=s16-demo-key $(IMAGE):local
	@echo "API on http://localhost:$(PORT)/"

stop:           ## Stop and remove the local container
	docker rm -f s16-calc 2>/dev/null || true

clean:          ## Remove build output and caches
	rm -rf build dist reports htmlcov .pytest_cache .coverage coverage.xml
