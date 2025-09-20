# The Weather

## Idea

*this section will be removed as the project gets closer to the idea laid out here*

Individual Python apps/services to request, transform, & store weather data from multiple sources. Starting with free/accessible APIs like [Open-Meteo](https://open-meteo.com) and [Weather API](https://www.weatherapi.com).

There should be a server/API (FastAPI or Django, most likely), which should be a simple REST API that listens for requests from the collectors, and sends the data to  be stored in the database.

The initial database will be PostgreSQL, but the project should eventually support MySQL/MariaDB.

Collectors will all have a local SQLite database that stores the raw responses from the API they're requesting.
