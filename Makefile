PROJECT_PACKAGE := machina
TEST_PACKAGE := tests


init:
	pipenv install --three --dev


# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to compile staticfiles, generate
# locales, build documentation, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: c console
## Alias of "console".
c: console
## Launch a development console.
console:
	pipenv run ipython

## Generates assets packaged with django-machina.
staticfiles:
	npm run gulp

## Generate the project's .po files.
messages:
	cd machina && pipenv run python -m django makemessages -a

## Compiles the project's .po files.
compiledmessages:
	cd machina && pipenv run python -m django compilemessages

.PHONY: docs
## Builds the documentation.
docs:
	cd docs && rm -rf _build && pipenv run make html


# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: qa
## Trigger all quality assurance checks.
qa: lint isort

.PHONY: lint
## Trigger Python code quality checks (flake8).
lint:
	pipenv run flake8

.PHONY: isort
## Check Python imports sorting.
isort:
	pipenv run isort --check-only --recursive --diff $(PROJECT_PACKAGE) $(TEST_PACKAGE)


# TESTING
# ~~~~~~~
# The following rules can be used to trigger tests execution and produce coverage reports.
# --------------------------------------------------------------------------------------------------

.PHONY: tests
## Run the Python test suite.
tests:
	pipenv run py.test

.PHONY: coverage
## Collects code coverage data.
coverage:
	pipenv run py.test --cov-report term-missing --cov $(PROJECT_PACKAGE)

.PHONY: spec
## Run the tests in "spec" mode.
spec:
	pipenv run py.test --spec -p no:sugar


# MAKEFILE HELPERS
# ~~~~~~~~~~~~~~~~
# The following rules can be used to list available commands and to display help messages.
# --------------------------------------------------------------------------------------------------

# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

.PHONY: help
## Print Makefile help.
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<action>${RESET}'
	@echo ''
	@echo 'Actions:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)-30s${RESET}\t${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -t'|' -sk1,1
