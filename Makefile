staticfiles:
	cd machina/static/machina && gulp build-application


.PHONY: install upgrade lint coverage travis docs

install:
	pip install -r dev-requirements.txt
	pip install -e .

upgrade:
	pip install -r dev-requirements.txt -U
	pip install -e . -U

lint:
	flake8

coverage:
	py.test --cov-report term-missing --cov machina

travis: install lint coverage

docs:
	cd docs && make html
