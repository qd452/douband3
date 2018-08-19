# douband3


## DB Migrate

https://flask-migrate.readthedocs.io/en/latest/


```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
$ python manage.py db --help
```

add movies from csv

`python3 manage.py add_movies_batch -c mv_detail.csv`