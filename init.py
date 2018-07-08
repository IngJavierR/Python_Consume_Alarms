import cron
import math, random
from flask import Flask, Response, json
from flask_cors import CORS
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
    return createResponse('Hello World')

@app.route('/alarms', methods=['GET'])
def getAlarms():
    alarms = createAlarms('am')
    alarms.extend(createAlarms('pm'))
    return createResponse(alarms)

def __main__():
    print('Iniciando Cron')
    #cron.start();
    print('Inicie Servicio')
    app.run()

__main__()