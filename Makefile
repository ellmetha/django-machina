.PHONY: install upgrade qa lint tests spec coverage travis docs


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
	cd machina && django-admin.py makemessages -a

# Compiles the project's .po files.
compiledmessages:
	cd machina && django-admin.py compilemessages

# Installs all the project's dependencies.
install:
	pip install -r requirements-dev.txt
	pip install -e .

# Upgrade all the project's dependencies.
upgrade:
	pip install -r requirements-dev.txt -U
	pip install -e . -U

# Builds the documentation.
docs:
	cd docs && rm -rf _build && make html


# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

qa: lint isort

# Code quality checks (eg. flake8, eslint, etc).
lint:
	flake8

# Import sort checks.
isort:
	isort --check-only --recursive --diff machina tests


# TESTING
# ~~~~~~~
# The following rules can be used to trigger tests execution and produce coverage reports.
# --------------------------------------------------------------------------------------------------

# Just runs all the tests!
tests:
	py.test

# Collects code coverage data.
coverage:
	py.test --cov-report term-missing --cov machina

# Run the tests in "spec" mode.
spec:
	py.test --spec -p no:sugar


# CONTINUOUS INTEGRATION
# ~~~~~~~~~~~~~~~~~~~~~~
# The following rules can be used to trigger operations that should be performed only in continuous
# integration environments.
# --------------------------------------------------------------------------------------------------

# Performs operations required to build & test the project on Travis CI.
travis: install qa coverage
