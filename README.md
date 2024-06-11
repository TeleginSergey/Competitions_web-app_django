# Information, which you can find at this website
Competitions and sports:

- one competition may include several sports
- a sport can be included in several competitions
- type of sport - name, description
- competition - name, start date, end date

Stages, competitions and sports:

- a competition for each sport may have several stages
- stage - name, date/time, place


# Library_django insruction

## Attention!
## Some commands can be diffirent depending on your OS and distributions
## This instruction was written for Linux Ubuntu


## Dependency installation
Intsall different python's frameworks and libraries on your computer (will be better if you will use venv)
```
pip install -r requirements.txt
```
Also you must download django through your package manager,
for example at Linux Ubuntu:
```
sudo apt install django
```

## Using venv (virtual enviroment)
Creating venv:
```
python -m venv <name_of_your_venv>
```
Activating venv:
```
source <name_of_your_venv>/bin/activate
```


## Launching a web application.
Additionally, to run this web application, you need to create a ".env" file and insert the following information:

```
PG_HOST=localhost
PG_PORT=48746
PG_USER=competition_user
PG_PASSWORD=competition_password
PG_DBNAME=competition_db
SECRET_KEY='django-insecure-co7b4e-2=#&n8b55t&ka*f)0re+fn(y_2eg1ux2okkz(95z_z='
```

Also you need to create a docker container for database:
```
docker run -d --name competition -p 48746:5432 -e POSTGRES_USER=competition_user -e POSTGRES_PASSWORD=competition_password -e POSTGRES_DB=competition_db postgres
```

After it, with this command
```
psql -h localhost -p 48746 -U competition_user competition_db
```
you will get into open-source relational database management system, there write:
```
create schema competition;
```
"\q" for quit.

after it you can write this commands:

* python3 manage.py makemigrations
* python3 manage.py migrate
* python3 manage.py runserver

Congratulations!!!

You can launch it later by simply typing the command:
- python3 manage.py runserver



## Launching tests command
- python3 manage.py test tests

Attention! If the tests are not passing, try renaming the folder "tests" to a different name, for example "testing". Accordingly, you will also need to change name "tests" in settings.py.

## Superuser
To enter the admin panel ('admin/'), you need to create a superuser. Here is the command for creating one:
- python3 manage.py createsuperuser

## Problems

### Logout
if you can't log out of your account on this web-app,
insert at templates/base_generic.html instead logout (delete whe whole 16 line) this code:
```
<form method="post" action="{% url 'logout' %}?next={{request.path}}">
    {% csrf_token %}
    <input type="submit" value="Logout">
</form>
```

Thanks for reading:)