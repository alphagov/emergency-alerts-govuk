.PHONY: build
build: clean
	npm run build
	python build.py

.PHONY: clean
clean:
	rm -rf dist/*

.PHONY: run
run: build
	cd dist && python -m http.server

.PHONY: bootstrap
bootstrap:
	pip install -r requirements_for_test.txt
	npm install

.PHONY: test
test:
	isort --check-only *.py
	flake8 .
