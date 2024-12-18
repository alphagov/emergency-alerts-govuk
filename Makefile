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

NVM_VERSION := 0.39.7
NODE_VERSION := 16.14.0

write-source-file:
	@if [ -f ~/.zshrc ]; then \
		if [[ $$(cat ~/.zshrc | grep "export NVM") ]]; then \
			cat ~/.zshrc | grep "export NVM" | sed "s/export//" > ~/.nvm-source; \
		else \
			cat ~/.bashrc | grep "export NVM" | sed "s/export//" > ~/.nvm-source; \
		fi \
	else \
		cat ~/.bashrc | grep "export NVM" | sed "s/export//" > ~/.nvm-source; \
	fi

read-source-file: write-source-file
	@if [ ! -f ~/.nvm-source ]; then \
		echo "Source file could not be read"; \
		exit 1; \
	fi

	@for line in $$(cat ~/.nvm-source); do \
		export $$line; \
	done; \
	echo '. "$$NVM_DIR/nvm.sh"' >> ~/.nvm-source;

	@if [[ "$(NVM_DIR)" == "" || ! -f "$(NVM_DIR)/nvm.sh" ]]; then \
		mkdir -p $(HOME)/.nvm; \
		export NVM_DIR=$(HOME)/.nvm; \
		curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v$(NVM_VERSION)/install.sh | bash; \
		echo ""; \
		$(MAKE) write-source-file; \
		for line in $$(cat ~/.nvm-source); do \
			export $$line; \
		done; \
		echo '. "$$NVM_DIR/nvm.sh"' >> ~/.nvm-source; \
	fi

	@current_nvm_version=$$(. ~/.nvm-source && nvm --version); \
	echo "NVM Versions (current/expected): $$current_nvm_version/$(NVM_VERSION)";

upgrade-node:
	@TEMPDIR=/tmp/node-upgrade; \
	if [[ -d $(NVM_DIR)/versions ]]; then \
		rm -rf $$TEMPDIR; \
		mkdir $$TEMPDIR; \
		cp -rf $(NVM_DIR)/versions $$TEMPDIR; \
		echo "Node versions temporarily backed up to: $$TEMPDIR"; \
	fi; \
	rm -rf $(NVM_DIR); \
	$(MAKE) read-source-file; \
	if [[ -d $$TEMPDIR/versions ]]; then \
		cp -rf $$TEMPDIR/versions $(NVM_DIR); \
		echo "Restored node versions from: $$TEMPDIR"; \
	fi;

.PHONY: install-nvm
install-nvm:
	@echo ""
	@echo "[Install Node Version Manager]"
	@echo ""

	@if [[ "$(NVM_VERSION)" == "" ]]; then \
		echo "NVM_VERSION cannot be empty."; \
		exit 1; \
	fi

	@$(MAKE) read-source-file

	@current_nvm_version=$$(. ~/.nvm-source && nvm --version); \
	if [[ "$(NVM_VERSION)" != "$$current_nvm_version" ]]; then \
		$(MAKE) upgrade-node; \
	fi

.PHONY: install-node
install-node: install-nvm
	@echo ""
	@echo "[Install Node]"
	@echo ""

	@. ~/.nvm-source && nvm install $(NODE_VERSION) \
		&& nvm use $(NODE_VERSION) \
		&& nvm alias default $(NODE_VERSION);

.PHONY: clean
clean:
	rm -rf dist/*

.PHONY: run-flask
run-flask:
	. environment.sh && flask run -p 6017

.PHONY: bootstrap
bootstrap: install-node
	pip3 install -r requirements_local_utils.txt
	. ~/.nvm-source && npm ci --no-audit && npm run build

.PHONY: bootstrap-for-tests
bootstrap-for-tests: install-node
	pip3 install -r requirements_github_utils.txt
	. ~/.nvm-source && npm ci --no-audit && npm run build

.PHONY: npm-audit
npm-audit:  ## Check for vulnerabilities in NPM packages
	. ~/.nvm-source && npm run audit

.PHONY: test
test:
	isort --check-only *.py app tests
	flake8 .
	. ~/.nvm-source npm run lint && npm test
	pytest tests/

.PHONY: freeze-requirements
freeze-requirements: ## create static requirements.txt
	pip3 install --upgrade pip-tools
	pip-compile requirements.in

.PHONY: run-celery
run-celery: ## Run celery
	. environment.sh && celery \
		-A run_celery.notify_celery worker \
		--uid=$(shell id -u easuser) \
		--pidfile=/tmp/celery.pid \
		--prefetch-multiplier=1 \
		--loglevel=WARNING \
		--concurrency=1 \
		--autoscale=8,1

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
