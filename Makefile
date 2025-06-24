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

.PHONY: generate-govuk-sha
generate-govuk-sha:
	pip3 install beautifulsoup4 requests && python scripts/generate_govuk_hash.py $(GOVUK_ALERTS_HOST_URL)/alerts | aws s3 cp - s3://govuk-sha-test/test.sha

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
		--autoscale=1,1
