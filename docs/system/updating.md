The Updating process depends on your chosen method of [installation](/install/docker)

While intermediate updates can be skipped when updating please make sure to
**read the release notes** in case some special action is required to update.

## Shopping pack sizes (migrations 0244–0246)

These migrations add pack/grams fields on foods (`shopping_measure`, `ingredient_unit_grams`,
`count_per_pack`, `shopping_measure_grams`) and `amount_grams` on shopping list entries.

0246 backfills `amount_grams` for existing entries when the food already has `shopping_measure_grams`.
Entries that cannot be converted are left unchanged (`amount_grams` stays null). The backfill also
clears invalid `count_per_pack` values below 1.

The new fields are additive. Rolling back means reversing the migrations; converted `amount`/`unit`
values on shopping entries are not restored. Take a backup before upgrading if you need a rollback path.

## Docker
For all setups using Docker the updating process look something like this

0. Before updating it is recommended to **create a [backup](/system/backup)!**
1. Stop the container using `docker compose down`
2. Pull the latest image using `docker compose pull`
3. Start the container again using `docker compose up -d`

## Manual

For all setups using a manual installation updates usually involve downloading the latest source code from GitHub.
After that make sure to run:

1. `pip install -r requirements.txt`
2. `manage.py collectstatic`
3. `manage.py migrate`
4. `cd ./vue`
5. `yarn install`
6. `yarn build`

To install latest libraries, apply all new migrations and collect new static files.

## PostgreSQL

Postgres does not automatically upgrade database files when you change versions and requires manual intervention.
One option is to manually [backup/restore](https://github.com/BrendenWalker/Stillroom/blob/develop/docs/system/updating.md#postgresql) the database.

A full list of options to upgrade a database provide in the [official PostgreSQL documentation](https://www.postgresql.org/docs/current/upgrading.html).

1.  Collect information about your environment.

``` bash
grep -E 'POSTGRES|DATABASE' ~/.docker/compose/.env
docker ps -a --format 'table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}' | awk 'NR == 1 || /postgres/ || /recipes/'
```

2. Export the stillroom database

``` bash
docker exec -t {{database_container}} pg_dumpall -U {{djangouser}} > ~/stillroom.sql
```

3. Stop the stillroom application
``` bash
docker compose down
```

4. Rename the stillroom volume

``` bash
mv ./postgresql ./postgresql.old
```

5. Update image tag on postgres container in the docker-compose.yaml

``` yaml
db_recipes:
  restart: always
  image: postgres:16-alpine
  volumes:
    - ./postgresql:/var/lib/postgresql/data
  env_file:
    - ./.env
```

6. Pull and rebuild database container

``` bash
docker compose pull && docker compose up -d db_recipes
```

7. Import the database export

``` bash
cat ~/stillroom.sql | docker exec -i {{database_container}} psql postgres -U {{djangouser}}
```

8. Install postgres extensions
``` bash
docker exec -it {{database_container}} psql postgres -U {{djangouser}}
```
  then
``` psql
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

If anything fails, go back to the old postgres version and data directory and try again.

There are many articles and tools online that might provide a good starting point to help you upgrade [1](https://thomasbandt.com/postgres-docker-major-version-upgrade), [2](https://github.com/tianon/docker-postgres-upgrade).
