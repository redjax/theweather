# API Server

Docker containers for the [`api-server` package](../../servers/api-server/). Serves the FastAPI app with Uvicorn.

## Overlays

The [`overlays/` directory](./overlays/) includes Docker Compose overlay files you can add to your `docker compose up` commands. This is useful for development to stand up a database or Redis cachee locally.

- [MySQL (mariadb)](./overlays/mariadb.yml)
- [PostgreSQL](./overlays/postgres.yml)
  - [pgAdmin](./overlays/pgadmin.yml)
  - [pgBackweb](./overlays/pgbackweb.yml)
- [Redis](./overlays/redis.yml)
  - [Redis Commander](./overlays/redis-commander.yml)
- [Temporal](./overlays/temporal.yml)

You can add these overlays to your command using `-f overlays/<overlay-file>.yml`.

For example, to start the API server with a Postgres and pgAdmin container, run:

```shell
docker compose -f compose.yml \ ## Always specify the main compose file
  -f overlays/postgres.yml \ ## Add the Postgres database container
  -f overlays/pgadmin.yml \ ## Add the pgAdmin container
  up -d
```
