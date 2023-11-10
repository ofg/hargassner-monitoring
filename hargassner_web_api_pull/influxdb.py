# (c) 2023, Oliver Graebner, oliver.graebner@zohomail.eu

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
import string
import re

class influxDB:

    def __init__(self, config : dict()):
        """
        Default constructor.
        """
        self.url = config['url']
        self.accessToken = config['access_token']
        self.org = config['org']
        self.bucketName = config['bucket_name']
        self.bucketDescription = "Stores values retrieved from Hargassner Web API"
        self.client = InfluxDBClient(url=self.url, token=self.accessToken, org=self.org)
        self.bucket = None

    
    def initBucket(self):
        """
        Creates the necessary bucket if it does not already exist.

        Returns:
        The bucket found / created or throws an excpetion in something went wrong.
        """
        bucketsApi = self.client.buckets_api()
        b = bucketsApi.find_bucket_by_name(self.bucketName)
        if b == None:
            logging.info(f"No bucket with name {self.bucketName} found")
            b = bucketsApi.create_bucket(bucket_name=self.bucketName, description=self.bucketDescription, org=self.org)
            logging.info(f'Created bucket "{b.name}" with id "{b.id}", retention policy "{b.retention_rules}"')
        else:
            logging.debug(f"Found bucket '{b.name}' with id '{b.id}'")
        self.bucket = b
        return b
    
    def __sanitizeString(self, str):
        """
        Replaces special characters (commas, spaces,... ) in a string so that it can be used as measurement name or tag
        """
        chars = re.escape(string.punctuation)
        chars = chars + " "
        newStr = re.sub('['+chars+']', '_', str)
        if str != newStr:
            logging.debug(f'Replaced string "{str}" with "{newStr}')
        return newStr


    def writeData(self, installation, subsystemData, timestamp):
        """
        Writes the given JSON data object to the bucket

        Paramters:
        installation Dictionary with installation data
        subsystemData List of sybsystems with their data (as dictionary) for the installation
        timestamp Seconds since epoch time.
        """
        writeApi = self.client.write_api()

        tags = installation.copy()
        tags['name'] = self.__sanitizeString(tags['name'])
        tags['id'] = str(tags['id'])
        
        for subsys in subsystemData:
            influxMeasurement = dict()
            influxMeasurement['measurement'] = self.__sanitizeString(subsys['name'])
            influxMeasurement['tags'] = tags
            influxMeasurement['fields'] = subsys['values']
            influxMeasurement['time'] = timestamp
            logging.debug(f'Data for writing: {influxMeasurement}')
            writeApi.write(self.bucketName, self.org, influxMeasurement, write_precision = 'ms')
            writeApi.flush()

        writeApi.close()

