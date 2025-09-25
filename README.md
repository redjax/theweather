# The Weather <!-- omit in toc -->

I use weather APIs to learn more about Python, git, and DevOps. This is another project to explore a monorepo architecture.

> [!WARNING]
> This README is incomplete until this message is removed

## Table of Contents <!-- omit in toc -->

- [Idea](#idea)
- [Repository](#repository)
  - [Filetree](#filetree)
  - [Paths](#paths)


## Idea

*this section will be removed as the project gets closer to the idea laid out here*

Individual Python apps/services to request, transform, & store weather data from multiple sources. Starting with free/accessible APIs like [Open-Meteo](https://open-meteo.com) and [Weather API](https://www.weatherapi.com).

There should be a server/API (FastAPI or Django, most likely), which should be a simple REST API that listens for requests from the collectors, and sends the data to  be stored in the database.

The initial database will be PostgreSQL, but the project should eventually support MySQL/MariaDB.

Collectors will all have a local SQLite database that stores the raw responses from the API they're requesting.

## Repository

The monorepo is divided into packages/applications that can be built & executed in a container, data pipelines for cleaning, transforming, & storing data, a shared package to provide domain objects & common setup/configurations, and more.

The [collectors](./collectors/) are isolated/independent Python packages that are built & executed inside a [Docker container](containers/weatherapi-collector/). This allows for doing a git sparse checkout of the `shared` and `weather-collector` packages so they can be built/run on another host, routing responses back to the central API server, or on the localhost for development.

### Filetree

<!-- MARK:REPO_TREE:START -->
```shell
.
├── shared
├── servers
│   └── api-server
├── scripts
│   └── docker
├── .sandbox
│   └── weatherapi_sandbox
├── .direnv
├── containers
│   ├── weatherapi-collector
│   └── container_data
└── collectors
    ├── weatherapi-collector
    └── openmeteo-collector
```
<!-- MARK:REPO_TREE:END -->

### Paths

> [!WARNING]
> This repository is in its early stages, and this list is likely incomplete/subject to change until this message is removed.

- [`.sandbox/`](./.sandbox/)
  - A testbed/prototyping area.
  - Import code from around the repository to demo it or test
  - Ignored in containers
- [`api-server`](./api-server/)
  - The central server collectors communicate with.
  - REST API implemented with FastAPI.
  - Stores metrics POSTed by collectors in the central database.
- [`collectors/`](./collectors/)
  - Isolated collection packages.
  - Encapsulate functionality to request weather data from an API & pass it to the API for storage.
  - Can be run on the local machine, or a remote machine with networking back to the API server host.
  - [`weatherapi-collector`](./collectors/weatherapi-collector/)
    - Collector package for the [WeatherAPI](https://www.weatherapi.com) REST API.
  - [`openmeteo-collector`](./collectors/openmeteo-collector/)
    - Collector package for the [OpenMeteo](https://open-meteo.com) REST API.
- [`containers/`](./containers/)
  - Dockerfiles & compose stacks for the apps.
  - Each collector has its own Dockerfile and `compose.yml` in this path, as well as a `.env` and a SQLite database for storing requests in case of interruptions in communication with the API server.
    - Saved responses have a `retain` boolean value, and once POSTed successfully it will be set to `False`.
    - Records are garbage collected on a schedule, re-trying any with `retain=True` and removing any with `retain=False`
  - This allows for running the app in its own container, for development or deployment.
  - (not implemented yet) stacks that orchstrate multiple containers.
- [`scripts/`](./scripts/)
  - Repository scripts, i.e. for [setting up the development environment after cloning to a new machine](./scripts/dev_setup.sh), scripts for [controlling Docker containers](./scripts/docker/), etc.
- [`shared/`](./shared/)
  - The `shared` Python package.
  - Provides shared configurations & code, like:
    - [`Dynaconf` settings](./shared/src/shared/config/)
    - [dependencies](./shared/src/shared/depends/)
    - [domain objects](./shared/src/shared/domain/)
    - [HTTP functionality](./shared/src/shared/http_lib/)
    - [setup code](./shared/src/shared/setup/)
      - i.e. shared [logging setup](./shared/src/shared/setup/_logging.py) for initializing `Loguru` using env vars.
