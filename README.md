# hargassner-monitoring
Monitoring of Hargassner heating while pulling data from Hargassner Web-API.

# Precondition

Data of your Hargassner heating installation has to be send to Hargassner via an 
Internet Gateway __AND__ you have to have an account for Hargassner WEB-APP / APP.

# System Deployment

![Deployment](./imgs/deployment.drawio.png)

* Hargassner heating installation with Internet Gateway sends data to Hargassner web service
* Python code  of `hargassner_web_api_pull` retrieves data and stores it into InfluxDB
* Data is visualized with Grafana Dashboards




# Required SW

* Python 3
* Poetry
* InfluxDB V2: I used the [manual installation option](https://docs.influxdata.com/influxdb/v2/install/?t=Linux#manually-download-and-install-the-influxd-binary), for development.

## InfluxDB

Configuration of development instance:

1. Start Influx DB
2. Open [Web-UI](http://localhost:8086) 
3. Create initial configuration with `user`, `password`, `org name`, `bucket name`
4. Save `Operator API Token` for later use.



## Poetry

Refer to [documentation for basic Poetry usage](https://python-poetry.org/docs/basic-usage/)


# Status value mappings

Defines the mapping of the string values for the status into numeric values for InfluxDB

### Heating Boiler (Heizungskessel) states

| State name | German meaning | Numberic value |
| --- | --- | --- |
| STATE_OFF | Aus | 0 |
| STATE_IGNITION | Zündung | 1 |
| STATE_EFFICIENCY_FIRE | Leistungsbrand | 2 |

### Buffer (Pufferspeicher) states

| State name | German meaning | Numberic value |
| --- | --- | --- |
| STATE_CHARGING | Ladung Puffer | ? |
| STATE_ON | ?? | ? |

### Heating Circuit (Heizkreis) states

| State name | German meaning | Numberic value |
| --- | --- | --- |
| STATE_OFF | Aus | 0 |
| STATE_HEATING | Heizen | ? |
| STATE_REDUCTION_TRANSITION | Absenken Rampe | ?



### Boiler (Heißwasserspeicher) states

| State name | German meaning | Numberic value |
| --- | --- | --- |
| STATE_OFF | Aus | 0 |

