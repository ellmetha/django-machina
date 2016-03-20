staticfiles:
	npm run gulp -- build-application


.PHONY: install upgrade lint coverage travis docs

install:
	pip install -r requirements-dev.txt
	pip install -e .

upgrade:
	pip install -r requirements-dev.txt -U
	pip install -e . -U

lint:
	flake8

coverage:
	py.test --cov-report term-missing --cov machina

travis: install lint coverage

docs:
	cd docs && rm -rf _build && make html
