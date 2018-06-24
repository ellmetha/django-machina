.PHONY: init install qa lint tests spec coverage docs


init:
	pipenv install --three --dev


# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to compile staticfiles, generate
# locales, build documentation, etc.
# --------------------------------------------------------------------------------------------------

# Generates assets packaged with django-machina.
staticfiles:
	npm run gulp

# Generate the project's .po files.
messages:
	cd machina && pipenv run python -m django makemessages -a

# Compiles the project's .po files.
compiledmessages:
	cd machina && pipenv run python -m django compilemessages

# Builds the documentation.
docs:
	cd docs && rm -rf _build && pipenv run make html


# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

qa: lint isort

# Code quality checks (eg. flake8, eslint, etc).
lint:
	pipenv run flake8

# Import sort checks.
isort:
	pipenv run isort --check-only --recursive --diff machina tests


# TESTING
# ~~~~~~~
# The following rules can be used to trigger tests execution and produce coverage reports.
# --------------------------------------------------------------------------------------------------

# Just runs all the tests!
tests:
	pipenv run py.test

# Collects code coverage data.
coverage:
	pipenv run py.test --cov-report term-missing --cov machina

# Run the tests in "spec" mode.
spec:
	pipenv run py.test --spec -p no:sugar
