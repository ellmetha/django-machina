PROJECT_PACKAGE := main
PROJECT_CONFIGURATION_PACKAGE := project
DJANGO_SETTINGS_MODULE := $(PROJECT_CONFIGURATION_PACKAGE).settings.dev

.PHONY: c console migrate migrations s server superuser


# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

c: console
console:
	pipenv run python manage.py shell --settings=$(DJANGO_SETTINGS_MODULE)

migrate:
	pipenv run python manage.py migrate --settings=$(DJANGO_SETTINGS_MODULE)

migrations:
	pipenv run python manage.py makemigrations --settings=$(DJANGO_SETTINGS_MODULE)

s: server
server:
	pipenv run python manage.py runserver 0.0.0.0:8000 --settings=$(DJANGO_SETTINGS_MODULE)

superuser:
	pipenv run python manage.py createsuperuser --settings=$(DJANGO_SETTINGS_MODULE)
