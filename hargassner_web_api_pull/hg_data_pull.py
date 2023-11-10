# (c) 2023, Oliver Graebner, oliver.graebner@zohomail.eu

import logging
import time
import yaml
import os
from datetime import datetime
from hg_web_api import hgWebApi
from influxdb import influxDB



def readYamlConfig() -> dict():
    """
    Reads the configuration from the config.yaml file and returns it as dictionary.
    Checks if all required information is given.
    """
    with open('config.yml', 'r') as file:
        configuration = yaml.safe_load(file)
    return configuration

def getLoggingLevel(config: dict()):
    """
    Get the logging level from the config or a default value if not set
    """
    ll = logging.INFO # that's the default if nothing is given
    if "log_level" in config:
        match config['log_level']:
            case "DEBUG":
                ll = logging.DEBUG
            case "INFO":
                ll = logging.INFO
            case "WARNING":
                ll = logging.WARNING
            case "ERROR":
                ll = logging.ERROR
            case "CRITICAL":
                ll = logging.CRITICAL
            case _:
                ll = logging.INFO
    return ll

        
config = readYamlConfig()
logging.basicConfig(level=getLoggingLevel(config), force=True, format='%(asctime)s %(levelname)s %(threadName)-10s: %(message)s')
startTime = datetime.utcnow()
logging.debug(f'Starting Hargassner Web-API data pull at {startTime}')

webApiInstance = hgWebApi(config['hargassner_web'])
webApiInstance.connectToServer()
influx = influxDB(config['influxdb'])
influx.initBucket()


installations = webApiInstance.requestInstallations()
for i in installations:
    jsonResponse = webApiInstance.pullData(i)
    # get timestamp since epoch in ms
    timestamp = round(time.time() * 1000)
    #jsonResponse = loadDataFromFile()
    subsystemData = webApiInstance.convertDataResponse(jsonResponse)
    logging.debug(f'Converted response: {subsystemData}')
    influx.writeData(i, subsystemData, timestamp)

endTime = datetime.utcnow()
duration = endTime - startTime
logging.warning(f'Web-API data pull took {duration.total_seconds()} s')



