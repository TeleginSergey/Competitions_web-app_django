Соревнования и виды спорта:

- одно соревнование может включать несколько видов спорта
- вид спорта может быть включен в несколько соревнований
- вид спорта - название, описание
- соревнование - название, дата начала, дата окончания

Этапы, соревнования и виды спорта:

- в соревновании по каждому виду спорта может быть несколько этапов
- этап - название, дата/время, место

## Install
```
pip install -r requirements.txt
```
```
sudo apt install django
```

## venv
Creating venv:
```
python -m venv <name_of_your_venv>
```
Activating venv:
```
source <name_of_your_venv>/bin/activate
```


## .env
```
PG_HOST=localhost
PG_PORT=48746
PG_USER=competition_user
PG_PASSWORD=competition_password
PG_DBNAME=competition_db
SECRET_KEY='django-insecure-co7b4e-2=#&n8b55t&ka*f)0re+fn(y_2eg1ux2okkz(95z_z='
TELEGIN_TOKEN = 10015ea89b0737ec129f31e7604a9f77b2d37604
```

## docker conrainer
```
docker run -d --name competition -p 48746:5432 -e POSTGRES_USER=competition_user -e POSTGRES_PASSWORD=competition_password -e POSTGRES_DB=competition_db postgres
```

## DB
```
psql -h localhost -p 5435 -U app library_db
```
```
create schema competition_schema;
```
