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

fmexp-layout1-frontend:
	cd fmexp/templates/frontend; yarn build-frontend1-production

fmexp-layout2-frontend:
	cd fmexp/templates/frontend; yarn build-frontend2-production

provision-layout1:
	ansible-playbook -i ansible/hosts ansible/provision-layout1.yml

provision-layout2:
	ansible-playbook -i ansible/hosts ansible/provision-layout2.yml

deploy-layout1:
	ansible-playbook -i ansible/hosts ansible/deploy-layout1.yml

deploy-layout2:
	ansible-playbook -i ansible/hosts ansible/deploy-layout2.yml
