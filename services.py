import json
import requests

primeProperties = {
    'headers': {'Content-Type': 'application/json',
            'Authorization': 'Basic Z3Vlc3Q6YXR0LjIwMTg='},
    'baseUrl': 'https://10.106.0.23/webacs/api/v1/',
    'paths': {
        'AllAlarms': 'data/Alarms.json?alarmFoundAt=gt("{0}")&.full=true'
    }
}

remedyPropesties = {
    'baseUrl': 'http://localhost/RemedyServices/',
    'paths': {
        'sendAlarm': 'api/tickets'
    }
}

def executeRequest(url):
    print(url)
    response = requests.get(url, headers=primeProperties['headers'], verify=False)
    return json.loads(response.content.decode('utf-8'))

def getAllAlarms(time):
    urlToExec = '{0}{1}'.format(primeProperties['baseUrl'], primeProperties['paths']['AllAlarms'].format(time))
    result = executeRequest(urlToExec)
    if 'entity' not in result['queryResponse']:
        return None
    return result['queryResponse']['entity']

def executeRemedyRequest(url, data):
    print(url)
    response = requests.post(url, data=data)
    return json.loads(response.content.decode('utf-8'))

def postAlarmRemedy(alarm):
    print('Sending')
    print(alarm)
    urlToExec = '{0}{1}'.format(remedyPropesties['baseUrl'], remedyPropesties['paths']['sendAlarm'])
    response = executeRemedyRequest(urlToExec, alarm)
    print(response)
    return response