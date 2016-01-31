staticfiles:
	cd machina/static/machina && gulp build-application


.PHONY: install upgrade lint coverage travis docs

install:
	pip install -r dev-requirements.txt
	pip install -e .

upgrade:
	pip install --upgrade -r dev-requirements.txt
	python setup.py develop --upgrade

lint:
	flake8

coverage:
	py.test --cov-report term-missing --cov machina

travis: install lint coverage

docs:
	cd docs && make html
