# populate.py

# Contains the getter functions for the Meteo API and preprocessing module. 
# It makes all relevant API calls to Meteo, preprocesses the results and finally dumps them
# into the database.

import pandas as pd
import logging
import datetime as dt
import sqlite3
from tabulate import tabulate
import sys
import os
from meteomatics._constants_ import LOGGERNAME
import meteomatics.api as api

DB_NAME = "meteo.db"
DUMMY = "./meteo_dummy.pkl"

username = os.environ.get("METEO_API_USR")
password = os.environ.get("METEO_API_PSW")

# logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(name)s:%(funcName)s: %(message)s', datefmt='%Y:%m:%d::%H:%M:%S')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
_logger.addHandler(stream_handler)

def check():
    """
    Function to check if getting close to the Meteo API limits and also display current count.

    Returns:
        None
    """
    res = api.query_user_limits(username, password)
    total0 = res['requests since last UTC midnight'][0]
    total1 = res['requests since last UTC midnight'][1] * 0.8
    sec0 = res['requests in the last 60 seconds'][0]
    sec1 = res['requests in the last 60 seconds'][1] * 0.8
    parallel0 = res['requests in parallel'][0]
    parallel1 = res['requests in parallel'][1] * 0.8
    if total0 >= total1:
        _logger.warning("CAUTION: approaching Meteo API limit. {} of {} total requests consumed".format(total0, total1))
    if sec0 >= sec1:
        _logger.warning("CAUTION: approaching Meteo API limit. {} of {} requests in the last 60 seconds consumed".format(sec0, sec1))
    if parallel0 >= parallel1:
        _logger.warning("CAUTION: approaching Meteo API limit. {} of {} parallel requests consumed".format(parallel0, parallel1))
    _logger.info("Requests total: {}/{}, last 60_sec: {}/{}, parallel: {}/{}".format(total0, int(total1), sec0, int(sec1), parallel0, int(parallel1)))

def getter():
    """
    Function to connect to the Meteo API (https://www.meteomatics.com/en/)
        and make API calls to gather all requested data.

    Returns:
        DataFrame that contains the preprocessed result of the API calls
    """

    check()
    startdate = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) # starting date
    enddate = startdate + dt.timedelta(days=7) # ending date
    interval = dt.timedelta(days=1) # interval
    coordinates = [
        (37.9839412, 23.7283052), # coords
    ]
    loc_dict = { # coords dict
        "Athens" : (37.9839412, 23.7283052),
        "Rethimno" : (35.3676472, 24.4736079),
        "Larnaca" : (4.9236095, 33.6236184)
    }
    model = 'mix' # forecasting model
    parameters = ['t_2m:C', 'precip_24h:mm', 'wind_speed_10m:ms'] # what to forecast
    _logger.info("Starting preprocessing")
    res = pd.DataFrame()
    temp = pd.DataFrame()
    # loop for every location in loc_dict
    for key, value in loc_dict.items(): 
        # make api call with defined parameters
        try:
            _logger.info("API call for {}".format(key))
            df = api.query_time_series([loc_dict[key]], startdate, enddate, interval,
                                  parameters, username, password)
        except Exception as e:
            _logger.error('Failed with exception {}'.format(e))

        # prepare the dataframe to insert to db
        loc = []
        lat = []
        lon = []
        date = []
        temp = []
        rain = []
        wind = []

        # unwrap the result of api call
        for i, (ind, val) in enumerate(zip(df.index, df.values)):
            loc.append(key)
            lat.append(ind[0])
            lon.append(ind[1])
            date.append(ind[2].date())
            temp.append(float(val[0]))
            rain.append(float(val[1]))
            wind.append(float(val[2]))
        temp = pd.DataFrame(list(zip(loc, lat, lon, date, temp, rain, wind)),
                                columns =['loc', 'lat', 'lon', 'date', 'temp', 'rain', 'wind'])
        _logger.info(f'finished getting {key}')
        
        # combining the different location dfs
        res = pd.concat([res, temp])

    # resetting index to use as PK later
    res.reset_index(drop=True, inplace=True)
    res.to_pickle(f"./meteo_dummy.pkl") # for backup
    _logger.info("result of getter: \n{}".format(res))
    return res

def preproc(df):
    """
    Function that takes as input the preprocessed DataFrame of the getter() function
        and puts it into a db.

    Args:
        df (pandas.DataFrame): DataFrame containing weather data

    Returns:
        None
    """
    #df = pd.read_pickle(DUMMY)
    #_logger.info("loaded dummy pickle file {}: \n{}".format(DUMMY, df))

    # connect to db
    def connect_to_db():
        try:
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          _logger.info("Connected to db: " + DB_NAME)
        except Exception as e:
          _logger.error("Failed with exception {}".format(e))
        return conn, cursor

    # create tables
    conn, cursor = connect_to_db()
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS `weather_data` (
        `index` integer PRIMARY KEY,
        `loc` string DEFAULT NULL,
        `lat` float DEFAULT NULL,
        `lon` float DEFAULT NULL,
        `date` timestamp DEFAULT NULL,
        `temp` float DEFAULT NULL,
        `rain` float DEFAULT NULL,
        `wind` float DEFAULT NULL,
        PRIMARY KEY (`lat`, `lon`)
      );
              ''')
    _logger.info("created SQL table")

    # send data to table
    df.to_sql('weather_data', conn, if_exists='replace', index=True)
    _logger.info('sent dataframe to db')

    # print table to make sure
    sql_query = """SELECT * FROM weather_data
        """
    cursor.execute(sql_query)
    names = list(map(lambda x: x[0], cursor.description))
    #_logger.info('Columns: {}'.format(names))
    res = cursor.fetchall()
    _logger.info('db table ↓\n{}'.format(tabulate(res, headers=names)))

def run():
    """
    Function to get called from outside this scope if this file gets imported as module.

    Returns:
        None
    """
    _logger.info("Running populate functions")
    df = getter()
    preproc(df)

def export():
    """
    Function to export database to csv.

    Returns:
        None
    """
    conn = sqlite3.connect(DB_NAME, isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM weather_data", conn)
    db_df.to_csv('meteo.csv', index=False)

if __name__ == "__main__":
    df = getter()
    preproc(df)
    check()
    #export()
