default: install

install: virtualenv

virtualenv:
	virtualenv env
	env/bin/pip install --upgrade -r requirements.txt

flask-run:
	FLASK_ENV=development FLASK_APP=fmexp env/bin/flask run --host=0.0.0.0 --port=5002

flask-shell:
	FLASK_ENV=development FLASK_APP=fmexp env/bin/flask shell

frontend1:
	cd fmexp/templates/frontend; yarn build-frontend1

frontend2:
	cd fmexp/templates/frontend; yarn build-frontend2
