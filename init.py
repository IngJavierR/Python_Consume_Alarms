import cron, persist
import math, random, datetime
from bson import json_util
from flask import Flask, Response, json
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
#Fine Alarms Every (minutes)
timeToSearchAlarms = 450

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

@app.route('/alarms', methods=['GET'])
def getAlarms():
    alarms = cron.job(timeToSearchAlarms)
    return createResponse(json_util._json_convert(alarms))

def __main__():
    print('Iniciando Cron')
    #cron.start(timeToSearchAlarms);
    print('Inicie Servicio')
    app.run()

__main__()