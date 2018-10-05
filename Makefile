# Virtual Environment
install:
	python3.6 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
install_package:
	venv/bin/pip install ${PKG}
	venv/bin/pip freeze > requirements.txt
freeze:
	venv/bin/pip freeze > requirements.txt

# Django
makemigrations:
	venv/bin/python manage.py makemigrations
migrate:
	venv/bin/python manage.py migrate
shell:
	venv/bin/python manage.py shell
startapp:
	venv/bin/python manage.py startapp ${APP}
createsuperuser:
	venv/bin/python manage.py createsuperuser
runserver:
	venv/bin/python manage.py runserver 0.0.0.0:8045
runprod:
	venv/bin/python manage.py check --deploy
	venv/bin/python manage.py collectstatic --noinput
	sudo venv/bin/gunicorn -w 3 --bind 0.0.0.0:8045 nodestack.wsgi