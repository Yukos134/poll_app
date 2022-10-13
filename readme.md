# to deploy the project

## start redis in docker:
* docker-compose up -d --build

## start django app on localhost:
* python -m pip install -r requirements.txt
* python manage.py makemigrations
* python manage.py migrate
* python manage.py runserver
* python manage.py createsuperuser

# api description:
* /polls or '' - get all polls
* /poll - create poll(poll_name: str, options: str with ';' delimiter, poll_duration_days: int)
* /vote - send opinion(poll_id: str, opinion_id: int)
