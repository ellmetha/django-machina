coverage:
		coverage --source=machina run ./runtests.py
		coverage report -m

css:
		# Compile CSS files from LESS
		lessc machina/static/machina/less/admin.less > machina/static/machina/css/admin.css
