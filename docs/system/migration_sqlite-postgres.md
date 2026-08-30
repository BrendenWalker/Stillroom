# How to migrate from sqlite3 to PostgreSQL

1. Back up your data directory (media files and the SQLite database).

2. Shell into the Stillroom container and export:

```
docker exec -it <stillroom_container> /bin/sh
cd /opt/recipes
./venv/bin/python manage.py export -a > /opt/recipes/mediafiles/dump.json
```

3. Create a PostgreSQL database and user.

4. Point Stillroom at PostgreSQL:

```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_HOST=<postgres host>
POSTGRES_PORT=5432
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<database>
```

5. Start the container so it runs migrations against PostgreSQL.

6. Import the dump:

```
docker exec -it <stillroom_container> /bin/sh
cd /opt/recipes
./venv/bin/python manage.py import /opt/recipes/mediafiles/dump.json
```
