.DEFAULT_GOAL := help
SHELL := /bin/bash
TIME = $(shell date +%Y-%m-%dT%H:%M:%S%z)

# Passed through by Dockerfile/buildspec
APP_VERSION ?= unknown

GIT_COMMIT ?= $(shell git rev-parse HEAD 2> /dev/null || echo "")

VIRTUALENV_ROOT := $(shell [ -z $$VIRTUAL_ENV ] && echo $$(pwd)/venv || echo $$VIRTUAL_ENV)
PYTHON_EXECUTABLE_PREFIX := $(shell test -d "$${VIRTUALENV_ROOT}" && echo "$${VIRTUALENV_ROOT}/bin/" || echo "")

.PHONY: clean
clean:
	rm -rf dist/*

.PHONY: run-flask
run-flask:
	. environment.sh && flask run -p 6017

.PHONY: run-flask-debug
run-flask-debug: ## Run flask in debug mode
	. environment.sh && flask --debug run -p 6017

.PHONY: bootstrap
bootstrap: generate-version-file
	pip3 install -r requirements_local_utils.txt
	npm ci --no-audit && npm run build

.PHONY: bootstrap-for-tests
bootstrap-for-tests: generate-version-file
	pip3 install -r requirements_github_utils.txt
	npm ci --no-audit && npm run build

.PHONY: npm-audit
npm-audit:  ## Check for vulnerabilities in NPM packages
	npm run audit

.PHONY: generate-version-file
generate-version-file: ## Generate the app/version.py file
	@ GIT_COMMIT=${GIT_COMMIT} TIME=${TIME} APP_VERSION=${APP_VERSION} envsubst < app/version.dist.py > app/version.py

.PHONY: test
test:
	isort --check-only *.py app tests
	flake8 .
	npm run lint && npm test
	pytest tests/

.PHONY: freeze-requirements
freeze-requirements: ## create static requirements.txt
	${PYTHON_EXECUTABLE_PREFIX}pip3 install --upgrade setuptools pip-tools
	${PYTHON_EXECUTABLE_PREFIX}pip-compile --strip-extras requirements.in

.PHONY: run-celery
run-celery: ## Run celery
	. environment.sh && opentelemetry-instrument celery \
		-A run_celery.notify_celery worker \
		--pidfile=/tmp/govuk_celery_worker.pid \
		--prefetch-multiplier=1 \
		--loglevel=INFO \
		--autoscale=8,1 \
		--hostname='govuk-alerts@%h'

.PHONY: uninstall-packages
uninstall-packages:
	python -m pip uninstall emergency-alerts-utils -y
	python -m pip freeze | xargs python -m pip uninstall -y
