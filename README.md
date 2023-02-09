# weather_api
A port of Meteomatics API with Flask, SQLAlchemy, Marshmallow and Connexion

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger) [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Table of Contents
1. [Usage](#usage)
2. [Pipeline](#pipeline)
3. [Files](#files)
4. [Endpoints](#endpoints)
5. [Logging](#logging)

## Usage <a name="usage"></a>

To use the API you have to create environment variables
with the names `METEO_API_USR` and `METEO_API_PSW`, for the username and password respectively, and then export the variables and source the script.

Example script is provided in `./creds_example`. Edit the username/password pair and remove the word `_example` from the filename. **Caution**: Do not upload `./creds`.

```lang-bash
>>> cp creds_example creds && source creds
```
To install the package requirements that are needed, run the following (ideally inside a venv):
```lang-bash
>>> pip install -r requirements.txt 
```

To run the application:
```lang-bash
>>> python app.py
```
which initiates the web-app at `0.0.0.0:8000` (`127.0.0.1:8000`). For additional info please see [Endpoints](#endpoints) (overview at `127.0.0.1:8000/api/ui`).

## Pipeline <a name="pipeline"></a>
- **Process**
    1. Signed up for the API (free tier) and got credentials.
    2. Read Meteo API documentation to decide which endpoints to use.
    3. Meteomatics has python wrapper lib so read up on that.
    4. Create sqlite database - I used sqlite and a simple table format due to the simplicity of the data. For scaling up this application another schema could be used: a table for each location we support OR a table for each day (due to the fact that the days are +/- set).  
    5. Preprocess data from meteo api into a dataframe.
    6. Insert dataframe to database.
    7. Create flask app, endpoints and functions.
    8. Connecting database to flask with sqlalchemy and marchmallow.
- **Problems/Limitations**
    - Unit testing is not implemented. The first thing that would be done given more time is implement unit testing with `pytest`.
    - Solution is not deployed to a cloud service.
    - Simple database schema.
    - If we need the API to run continuously, this could be easily added with a `cronjob` that runs `populate.py` and updates the database.
    - General: due to this being my first implementation of an API (usually until now I only had to ingest data) some best practices might now be present. However despite this being a challenge to learn and implement in a short period of time, I am glad to have learned a new skill.
- **Tools**
    - `marshmallow` for serialization/deserialization.
    - `flask` for the core web-app.
    - `sqlalchemy` for DB connection (object-relational model (ORM))
    - `Connexion` for endpoint configuration.
## Files <a name="files"></a>
- `app.py`
	- API top level runner - initializes the API and sets up the relevant config files.
- `swagger.yml`
	- Contains OpenAPI definitions and all of the information necessary to configure server to provide input parameter validation, output response data validation, and URL endpoint definition.
- `weather.py`
	- Contains the functions that get called from the endpoints.
- `templates/`
	- `/templates/home.html`
		- homepage that that gets rendered on endpoint `/` and displays all weather data in an HTML list.
- `config.py`
	- Gets the necessary modules imported and configured, including Flask, Connexion, SQLAlchemy, and Marshmallow. It sets up the connections to the database, sets up Marshmallow for JSON serialization and SQLAlchemy for the database interaction.
- `models.py`
	- Defining the class models that are needed for the database interaction for SQLAlchemy and Marshmallow.
- `populate.py`
	- Contains the getter functions for the Meteo API and preprocessing module. It makes all relevant API calls to Meteo, preprocesses the results and finally dumps them into the database.
- `config_example`
	- Contains environment variables to set up the source API from Meteo.
- `meteo.db`
	- Database file.

## Endpoints <a name="endpoints"></a>
- `/`
    - list all weather in a HTML list
- `/{location}/`
	- JSON all weather for {location} for every day
	- {location} in {"Athens", "Rethimno", "Larnaca"}
- `{location}/{day}`
	- JSON all weather for {location} for {day}
	- {day} in format {YYYYMMDD} i.e. 20230210
- `{location}/{day}/average`
	- integer 3-day rolling average temp
- `/top/{metric}/{n}`
	- JSON top {n} locations for every day for {metric}
	- {metric} in {"temp", "rain", "wind"}
- `/api/ui`
    - overview of API endpoints and testing.  

# Logging <a name="logging"></a>
| Level      | When it is used |
| ----------- | ----------- |
| DEBUG      | Detailed information, typically of interest only when diagnosing problems.|
| INFO      | Confirmation that things are working as expected.|
| WARNING      | An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.|
| ERROR   | Due to a more serious problem, the software has not been able to perform some function.|
| CRITICAL      | A serious error, indicating that the program itself may be unable to continue running.|
