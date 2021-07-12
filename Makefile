.DEFAULT_GOAL := help
SHELL := /bin/bash

CF_API ?= api.cloud.service.gov.uk
CF_ORG ?= govuk-notify
CF_SPACE ?= ${DEPLOY_ENV}
CF_HOME ?= ${HOME}
CF_APP ?= notify-govuk-alerts
CF_MANIFEST_PATH ?= /tmp/manifest.yml
NOTIFY_CREDENTIALS ?= ~/.notify-credentials
$(eval export CF_HOME)

.PHONY: build
build: clean
	npm run build
	python build.py

.PHONY: clean
clean:
	rm -rf dist/*

.PHONY: run
run: build
	python main.py

.PHONY: bootstrap
bootstrap:
	pip install -r requirements_for_test.txt
	npm ci

.PHONY: test
test:
	isort --check-only *.py lib tests
	flake8 .
	npm run lint
	npm test
	pytest tests/

.PHONY: cf-login
cf-login: ## Log in to Cloud Foundry
	$(if ${CF_USERNAME},,$(error Must specify CF_USERNAME))
	$(if ${CF_PASSWORD},,$(error Must specify CF_PASSWORD))
	$(if ${CF_SPACE},,$(error Must specify CF_SPACE))
	@echo "Logging in to Cloud Foundry on ${CF_API}"
	@cf login -a "${CF_API}" -u ${CF_USERNAME} -p "${CF_PASSWORD}" -o "${CF_ORG}" -s "${CF_SPACE}"

.PHONY: generate-manifest
generate-manifest: check-env-vars
	$(if ${CF_APP},,$(error Must specify CF_APP))
	$(if ${CF_SPACE},,$(error Must specify CF_SPACE))
	$(if $(shell which gpg2), $(eval export GPG=gpg2), $(eval export GPG=gpg))
	$(if ${GPG_PASSPHRASE_TXT}, $(eval export DECRYPT_CMD=echo -n $$$${GPG_PASSPHRASE_TXT} | ${GPG} --quiet --batch --passphrase-fd 0 --pinentry-mode loopback -d), $(eval export DECRYPT_CMD=${GPG} --quiet --batch -d))

	jinja2 --strict manifest.yml.j2 \
	    -D environment=${CF_SPACE} \
	    -D cf_app_name=${CF_APP} \
	    --format=yaml \
	    <(${DECRYPT_CMD} ${NOTIFY_CREDENTIALS}/credentials/${CF_SPACE}/paas/environment-variables.gpg) 2>&1

.PHONY: check-env-vars
check-env-vars: ## Check mandatory environment variables
	$(if ${DEPLOY_ENV},,$(error Must specify DEPLOY_ENV))

.PHONY: cf-target
cf-target: check-env-vars
	@cf target -o ${CF_ORG} -s ${CF_SPACE}

.PHONY: cf-deploy
cf-deploy: cf-target ## Deploys the app to Cloud Foundry
	@cf app --guid ${CF_APP} || exit 1
	# cancel any existing deploys to ensure we can apply manifest (if a deploy is in progress you'll see ScaleDisabledDuringDeployment)
	cf cancel-deployment ${CF_APP} || true

	# generate manifest (including secrets) and write it to CF_MANIFEST_PATH (in /tmp/)
	make -s CF_APP=${CF_APP} generate-manifest > ${CF_MANIFEST_PATH}
	# reads manifest from CF_MANIFEST_PATH
	CF_STARTUP_TIMEOUT=10 cf push ${CF_APP} --strategy=rolling -f ${CF_MANIFEST_PATH}
	# delete old manifest file
	rm -f ${CF_MANIFEST_PATH}

.PHONY: preview
preview: ## Set environment to preview
	$(eval export DEPLOY_ENV=preview)
	@true

.PHONY: production
production: ## Set environment to production
	$(eval export DEPLOY_ENV=production)
	@true
