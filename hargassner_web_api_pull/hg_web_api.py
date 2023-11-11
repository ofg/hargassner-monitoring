# (c) 2023, Oliver Graebner, oliver.graebner@zohomail.eu

import requests
import json

import log
logger = log.getGlobalLogger()

class hgWebApi:

    def __init__(self, config : dict()):
        """
        Default constructor.

        """
        self.url = config['url']
        self.email = config['email']
        self.password = config['password']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.accessTokon = None
        self.refreshToken = None
        self.expiresIn = None

    def __getHeaders(self):
        """
        Generate headers used for REST access including authorization.
        """
        authHeader = "Bearer " + self.accessToken
        return { "Accept": "application/json", "Authorization": authHeader}

    def connectToServer(self):
        """
        Authenticates against the server with configured username / password and stores access token for subsequent use.
        """
        r = requests.post(f'{self.url}/api/auth/login', json={"email":self.email,"password":self.password,"client_id":str(self.client_id),"client_secret":self.client_secret})
        if r.status_code == 200:
            logger.debug(f'Logged into {self.url}')
            if r.json()['token_type'] != "Bearer":
                tokenType = r.json()['token_type']
                logger.error(f'Received token type {tokenType} instead of "Bearer"')
                raise Exception(f'Received token type {tokenType} instead of "Bearer"')
            self.accessToken = r.json()['access_token']
            self.refreshToken = r.json()['refresh_token']
            self.expiresIn = r.json()['expires_in']
            logger.debug(f'Received access and refresh token for {self.url}, token expires in {self.expiresIn}')
            
        else:
            raise Exception(f'Failed to log into {self.url}: status code is {r.status_code}')
        
    def requestInstallations(self):
        """
        Requests installation for logged in users and collects installation id and slug
        """
        r = requests.get(
            f'{self.url}/api/installations?with=devices.gateway%3Bcreator&sort=name&pageSize=100&page=1',
            headers = self.__getHeaders()
        )
        if r.status_code == 200:
            logger.debug(f'Received list of installations from server:')
            installations = list()
            for installation in r.json()['data']:
                item = dict()
                item['id'] = installation['id']
                item['slug'] = installation['slug']
                item['name'] = installation['name']
                installations.append(item)
                logger.debug(f"{len(installations)} - {item['name']}, {item['id']}, {item['slug']}")
            return installations
        else:
            raise Exception(f'Failed to retrieve installations for user: status code is {r.stats_code}')
        

    def pullData(self, installation): 
        """
        Returns the JSON encoded response - if any.

        Parameters:
        installation - JSON object of single installation from the list returned by requestInstallations()
        """
        r = requests.get(
            f"{self.url}/api/installations/{installation['id']}/widgets",
            headers = self.__getHeaders()
        )
        if r.status_code == 200:
            data = json.dumps(r.json())
            logger.debug(f'Data received for {installation["name"]}: {data}')
            return r.json()

        else:
            logger.error('Failed to pull data from web api, status code is {r.status_code}')
            raise Exception('Failed to pull data from web api, status code is {r.status_code}')
        
    def convertStateValues(self, stateName : str) -> int:
        """
        Converts state strings into numeric values.
        """
        x = 0
        match stateName:
            # state of boiler, heating circuit, heating boiler
            case 'STATE_OFF':
                x = 0
            # state of heating boiler
            case 'STATE_IGNITION':
                x = 1
            case 'STATE_EFFICIENCY_FIRE':
                x = 2
            case 'STATE_DEASHING':
                x = 3
            # state of buffer
            case 'STATE_CHARGING':
                x = 10
            case 'STATE_ON':
                x = 11
            # state of heating circuit
            case 'STATE_HEATING':
                x = 20
            case 'STATE_REDUCTION_TRANSITION':
                x = 21
            case _:
                logger.warn(f'No numeric state matching defined for string {stateName}')
                x = -1
        logger.info(f'Mapping state value from {stateName} to {x}')
        return x


        
    def convertWidgetValues(self, widget : json):
        """
        Extract key/value pairs from the widget - except name and device_type - and puts it into a 
        a dictionary

        Returns:
        Dictionary with key / value pairs.
        """
        values = dict()
        for k,v in widget['values'].items():
            # Name element has already been handled!
            if k != "name" and k != "device_type":
                if v == None:
                    logger.info(f'Dropping key {k} as value is None')
                elif isinstance(v, bool):
                    if v:
                        values[k] = 1
                    else:
                        values[k] = 0
                elif isinstance(v, int):
                    # convert all ints to floats, otherwise values may switch between floats and ints if 
                    # fractional digits are 0 which causes an error in InfluxDB
                    values[k] = float(v)
                elif isinstance(v, str):
                    if k == 'state':
                        values[k] = self.convertStateValues(v)
                    else:
                        logger.info(f'Dropping key {k} as value is a string: {v}')
                else:
                    values[k] = v
        if len(values) <= 0:
            raise Exception("Failed to get values for widget: " + json.dumps(widget))
        else:
            logger.debug(f"Extracted widget values: {values}")

        return values
    
    def extractWidgetName(self, widget):
        """
        Extracts the name of the widget from its JSON object
        """
        # if there is no name, I use the widget type as name
        name = ""
        try:
            if len(widget['values']['name']) > 0:
                name = widget ['values']['name']
            else:
                name = widget['widget']
        except KeyError:
            name = widget['widget']


        if name == None or name == "":
            raise Exception("Failed to get name for widget: " + json.dumps(widget))
        else:
            logger.debug(f"Extracted widget name is {name}")
        
        return name
    
    def convertDataResponse(self, jsonResponse : json):
        """
        Converts the JSON response from the API call to a list of widgets with name / values
        """
        convertedResponse = list()

        for widget in jsonResponse['data']:
            convertedWidget = dict()
            convertedWidget['name'] = self.extractWidgetName(widget)
            convertedWidget['values'] = self.convertWidgetValues(widget)
            convertedResponse.append(convertedWidget)
        return convertedResponse




    