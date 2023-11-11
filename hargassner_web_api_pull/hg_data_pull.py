# (c) 2023, Oliver Graebner, oliver.graebner@zohomail.eu

import log
logger = log.setupGlobalLogger()

from datetime import datetime
import time
import yaml
import os

from hg_web_api import hgWebApi
from influxdb import influxDB



def readYamlConfig() -> dict():
    """
    Reads the configuration from the config.yaml file and returns it as dictionary.
    Checks if all required information is given.
    """
    fName = 'config.yml'
    logger.debug(f'Searching for {fName} in directory {os.getcwd()}')
    with open(fName, 'r') as file:
        configuration = yaml.safe_load(file)
        logger.debug(f'Loaded configuration from {fName}')
    return configuration



try: 

    startTime = datetime.utcnow()
    logger.debug(f'Starting Hargassner Web-API data pull at {startTime}')
            
    config = readYamlConfig()

    # now set the console handler for logging according to config
    cll = log.getLoggingLevelFromConfig(config)
    if cll >= 0:
        log.configureStreamLogging(cll)
    else:
        logger.debug(f'Switching off console logging as "log_level" is not defined in config')


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
        logger.debug(f'Converted response: {subsystemData}')
        influx.writeData(i, subsystemData, timestamp)

    endTime = datetime.utcnow()
    duration = endTime - startTime
    logger.debug(f'Web-API data pull took {duration.total_seconds()} s')

except:
    logger.exception(f'Unrecoverabe error occured - termintating Web-API data pull')



