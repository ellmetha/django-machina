css:
		# Compile CSS files from LESS
		lessc machina/static/machina/less/admin.less > machina/static/machina/css/admin.css
		lessc machina/static/machina/less/styles.less > machina/static/machina/css/styles.css


.PHONY: install upgrade coverage travis

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
