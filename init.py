import cron, persist, services
import math, random, datetime
from bson import json_util
from flask import Flask, Response, json
from flask_cors import CORS
import time, atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

#Fine Alarms Every (minutes)
timeToSearchAlarms = 5

def cron_start():
    print('Iniciando Cron')
    cron.start(timeToSearchAlarms)

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=cron_start,
    trigger=IntervalTrigger(minutes=timeToSearchAlarms),
    id='search-alarms',
    name='Search Prime Alarms',
    replace_existing=True)
atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)
CORS(app)

def createResponse(data):
    return Response(
        response=json.dumps(data),
        status=200,
        mimetype='application/json')

def createAlarms(timeId):
    return list(map(lambda x: (
        {
            "id": x,
            "hour": '12{0}'.format(timeId) if x== 0 else '{0}{1}'.format(x,timeId),
            "numTickets": math.floor(random.random() * 100) + 1
        }
    ), range(0,12)))

@app.route('/', methods=['GET'])
def hello_world():
    time = datetime.datetime.now()
    srtTime = time.strftime('%Y-%m-%dT%H')
    return createResponse(srtTime)

@app.route('/tickets', methods=['GET'])
def getTickets():
    time = datetime.datetime.now()
    day = time.strftime('%Y-%m-%dT')
    alarms =  persist.getAllAlarmsCounter(day)
    print("alarms")
    print(alarms)
    return createResponse(json_util._json_convert(alarms))

@app.route('/alarms/<int:time>', methods=['GET'])
def getAlarms(time):
    alarms = cron.alarms(time)
    return createResponse(json_util._json_convert(alarms))

@app.route('/device/<id>', methods=['GET'])
def getDeviceInfo(id):
    deviceInfo = services.getDeviceInfo(id)
    filterDeviceInfo = list(map(lambda x: (
        {
            "fans": x['inventoryDetailsDTO']['fans'],
            "ipInterfaces": x['inventoryDetailsDTO']['ipInterfaces'],
            "sensors": x['inventoryDetailsDTO']['sensors'],
            "summary": x['inventoryDetailsDTO']['summary'],
            "powerSupplies": x['inventoryDetailsDTO']['powerSupplies']
        }
    ), deviceInfo))
    return createResponse(json_util._json_convert(filterDeviceInfo))

def __main__():
    cron.start(timeToSearchAlarms)
    print('Inicie Servicio')
    app.run(host= '0.0.0.0')

__main__()