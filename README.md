# The Weather <!-- omit in toc -->

I use weather APIs to learn more about Python, git, and DevOps. This is another project to explore a monorepo architecture.

> [!WARNING]
> This README is incomplete until this message is removed

## Table of Contents <!-- omit in toc -->

- [Idea](#idea)
- [Repository](#repository)


## Idea

*this section will be removed as the project gets closer to the idea laid out here*

Individual Python apps/services to request, transform, & store weather data from multiple sources. Starting with free/accessible APIs like [Open-Meteo](https://open-meteo.com) and [Weather API](https://www.weatherapi.com).

There should be a server/API (FastAPI or Django, most likely), which should be a simple REST API that listens for requests from the collectors, and sends the data to  be stored in the database.

The initial database will be PostgreSQL, but the project should eventually support MySQL/MariaDB.

Collectors will all have a local SQLite database that stores the raw responses from the API they're requesting.

## Repository

The monorepo is divided into packages/applications that can be built & executed in a container, data pipelines for cleaning, transforming, & storing data, a shared package to provide domain objects & common setup/configurations, and more.

The [collectors](./collectors/) are isolated/independent Python packages that are built & executed inside a [Docker container](containers/weatherapi-collector/). This allows for doing a git sparse checkout of the `shared` and `weather-collector` packages so they can be built/run on another host, routing responses back to the central API server, or on the localhost for development.
