# weather.py

# contains the functions that get called from the endpoints:
# get_all_weather()
# get_loc()
# get_loc_day()
# get_loc_day_average()

import random
from flask import abort
import logging
from config import db
from models import Weather, weather_schema, weather_mult_schema
import datetime as dt
import sqlalchemy as sq
from sqlalchemy import and_, desc
import sys

# logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(name)s:%(funcName)s: %(message)s', datefmt='%Y:%m:%d::%H:%M:%S')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
_logger.addHandler(stream_handler)

logging.getLogger().setLevel(logging.DEBUG)

def get_all_weather():
    """
    Queries the db and returns all weather data

    Args:
        arr (ist): the list over which to search

    Returns:
        JSON of all weather
    """
    weather = Weather.query.all() # query from db
    return weather_mult_schema.dump(weather) # serialize

def get_loc(loc):
    """
    Queries the db and returns all weather data for {loc}

    Args:
        loc (string): the location to search for
            loc in ['Athens', 'Rethimno', 'Larnaca']

    Returns:
        JSON of all weather for {loc}
    """

    weather = Weather.query.filter(Weather.loc == loc)
    res = weather_mult_schema.dump(weather)
    if res is None:
        abort(406, f"{loc} is not in the list of locations")
    return res

def get_loc_day(loc, day):
    """
    Queries the db and returns all weather data for {loc} for {day}

    Args:
        loc (string): the location to search for
            loc in ['Athens', 'Rethimno', 'Larnaca']
        day (string): the day to search for
            day format YYYYMMDD i.e. 20230205

    Returns:
        JSON of all weather for {loc} and {day}
    """
    day = dt.datetime.strptime(day, '%Y%m%d').date()
    weather = Weather.query.filter(Weather.loc == loc).filter(Weather.date == day)
    res = weather_mult_schema.dump(weather)
    if res is None:
        abort(406, f"{loc} or {day} is not in the list of locations, days")
    return res

def get_loc_day_average(loc, day):
    """
    Queries the db and returns average temperature for {loc} 
        between {day} and 3 days before

    Args:
        loc (string): the location to search for
            loc in ['Athens', 'Rethimno', 'Larnaca']
        day (string): the end day to start calculating 3 days average 
            day format YYYYMMDD i.e. 20230205

    Returns:
        interger for average temperature for {loc} 
            between {day} and 3 days before
    """
    day = dt.datetime.strptime(day, '%Y%m%d').date()
    end = day - dt.timedelta(days=3)
    weather = Weather.query.filter(Weather.loc == loc).filter(and_(Weather.date <= day, Weather.date > end))
    res = weather_mult_schema.dump(weather)
    '''
    return {f"Average temp between {day} and {end}" :
            round((res[0]["temp"] + res[1]["temp"] + res[2]["temp"])/3, 2)
           }
    '''
    if res is None:
        abort(406, f"result no available")
    return round((res[0]["temp"] + res[1]["temp"] + res[2]["temp"])/3, 2)

def top(metric, n):
    """
    Queries the db and returns top {n} {metric}

    Args:
        metric (string): the metric to search for
            loc in ['temp', 'rain', 'wind']
        n (int): the number of returning results
            n <= 3

    Returns:
        JSON for top {n} results for {metric}
    """
    if isinstance(int(n), int) and (n <= 3):
        if metric == "temp": 
            weather = Weather.query.order_by(desc(Weather.temp)).limit(n).all()
            return weather_mult_schema.dump(weather)
        if metric == "rain": 
            weather = Weather.query.order_by(desc(Weather.rain)).limit(n).all()
            return weather_mult_schema.dump(weather)
        if metric == "wind": 
            weather = Weather.query.order_by(desc(Weather.wind)).limit(n).all()
            return weather_mult_schema.dump(weather)
        else:
            abort(404, "metric not found")
    else:
        abort(406, f"{n} is not int")

