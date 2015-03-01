css:
		# Compile CSS files from LESS
		lessc machina/static/machina/less/admin_theme.less > machina/static/machina/css/admin_theme.css
		lessc machina/static/machina/less/board_theme.less > machina/static/machina/css/board_theme.css


.PHONY: install upgrade coverage travis docs

install:
		pip install -r requirements.txt
		python setup.py develop

upgrade:
		pip install --upgrade -r requirements.txt
		python setup.py develop --upgrade

coverage:
		coverage run --source=machina ./runtests.py
		coverage report -m

travis: install coverage

docs:
	cd docs && make html
