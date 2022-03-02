default: install

install: virtualenv

virtualenv:
	virtualenv env
	env/bin/pip install --upgrade -r requirements.txt

flask-run:
	FLASK_ENV=development FLASK_APP=fmexp env/bin/flask run --host=0.0.0.0 --port=5002

flask-shell:
	FLASK_ENV=development FLASK_APP=fmexp env/bin/flask shell

frontend:
	cd fmexp/templates/frontend; yarn

fmexp1-frontend:
	cd fmexp/templates/frontend; yarn build-frontend1-production

fmexp2-frontend:
	cd fmexp/templates/frontend; yarn build-frontend2-production

provision-layout1:
	ansible-playbook ansible/provision-layout1

provision-layout2:
	ansible-playbook ansible/provision-layout2

deploy-layout1:
	ansible-playbook ansible/deploy-layout1

deploy-layout2:
	ansible-playbook ansible/deploy-layout2
