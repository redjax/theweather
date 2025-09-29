# Containers <!-- omit in toc -->

Docker containeres & Docker Compose stacks for development & "production" deployment. Because this is a monorepo, all containers are stored centrally here, separate from their app.

## Table of Contents <!-- omit in toc -->

- [Container Directories](#container-directories)
  - [API Server](#api-server)
  - [Databases](#databases)
  - [Schedulers](#schedulers)

## Container Directories

### API Server

- [`api-server/`](./api-server/)
  - Container stack for the [`api-server` package](../servers/api-server/)
  - Runs the FastAPI server with Uvicorn
  - The server waits for POST requests from one of the [collectors](../collectors/) and handles storing the raw request data centrally
  - (not implemented yet) Exposes endpoints to retrieve weather data from the central database

### Databases

- [`databases/`](./databases/)
  - Database containers for app backends
    - [PostgreSQL](./databases/postgres/) / [pgAdmin](./databases/pgadmin/)
    - [MySQL (mariadb)](./databases/mariadb/)
    - [InfluxDB](./databases/influxdb/)
    - [Redis](./databases/redis/)
  - These stacks can be run locally for development, or individually as nodes in the network

### Schedulers

- [`scheduleres`](./schedulers/)
  - Central scheduler servers
    - [`temporal`](./schedulers/temporal/)
- [`weatherapi-collector`](./weatherapi-collector/)
  - Container for the [WeatherAPI collector app](../collectors/weatherapi-collector/)
  - Polls [weatherapi.com](https://www.weatherapi.com) every 15 minutes to get the current & forecast weather
  - When `DYNACONF_WEATHERAPI__RUN_SCHEDULE=True`, starts a schedule using one of the included scheduler libraries
    - `DYNACONF_WEATHEREAPI__SCHEDULER=schedule_lib` starts a schedule using the [`schedule` Python package](https://pypi.org/project/schedule/)
    - `DYNACONF_WEATHEREAPI__SCHEDULER=apschedule_lib` starts a schedule using the [`APSchedule` Python package](https://pypi.org/project/APScheduler/)
  - Scheduler libraries all share the same schedule, hardcoded in the app. I *may* switch this to JSON files or environment variables later
