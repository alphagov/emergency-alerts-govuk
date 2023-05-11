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

.PHONY: clean
clean:
	rm -rf dist/*

.PHONY: run-flask
run-flask:
	FLASK_ENV=development flask run -p 6017

.PHONY: bootstrap
bootstrap:
	pip3 install -r requirements_for_test.txt
	source $(HOME)/.nvm/nvm.sh && nvm install && npm ci --no-audit && npm run build

.PHONY: npm-audit
npm-audit:  ## Check for vulnerabilities in NPM packages
	source $(HOME)/.nvm/nvm.sh && npm run audit

.PHONY: test
test:
	isort --check-only *.py app tests
	flake8 .
	source $(HOME)/.nvm/nvm.sh && npm run lint && npm test
	pytest tests/

.PHONY: freeze-requirements
freeze-requirements: ## create static requirements.txt
	pip install --upgrade pip-tools
	pip-compile requirements.in

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

cf-run-task-publish: cf-target
	cf run-task notify-govuk-alerts -c 'flask publish'
	# run a shell to setup a command to check progress;
	# "eval" is hacky way of assigning some text we want
	# to substitute later - by evaluating what follows as
	# a mini makefile and merging its state with this one
	$(eval \
		CHECK_COMMAND := cf curl "/v3/apps/`cf app --guid notify-govuk-alerts`/tasks?order_by=-created_at" | jq -r ".resources[0].state" \
	)
	# run a little shell script to check if the task is
	# successful and return a non-zero status if not;
	# make doesn't support multiline scripts, so the "\"
	# and ";" turn it into a oneliner with an exit status
	for _ in {1..36}; do \
		if $(CHECK_COMMAND) | grep SUCCEEDED; then\
			exit 0; \
		fi; \
		sleep 10; \
	done; \
	echo Command did not succeed in time! the last status of the task was $CHECK_COMMAND >&2; \
	cf logs notify-govuk-alerts --recent; \
	exit 1

.PHONY: preview
preview: ## Set environment to preview
	$(eval export DEPLOY_ENV=preview)
	@true

.PHONY: staging
staging: ## Set environment to staging
	$(eval export DEPLOY_ENV=staging)
	@true

.PHONY: production
production: ## Set environment to production
	$(eval export DEPLOY_ENV=production)
	@true
