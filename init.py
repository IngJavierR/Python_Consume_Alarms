import persist
import services
import datetime

#Fine Alarms Every (seconds)
timeToSearchAlarms = 5400

def filterAlarms(alarms):
    print(alarms)
    print('Filter')
    filteredAlarms = list(filter(lambda x: (
        x['alarmsDTO']['severity'] == 'CLEARED' or
        x['alarmsDTO']['severity'] == 'CRITICAL'
    ), alarms))
    return filteredAlarms

def getNewAlarms(time):
    primeAlarms = services.getAllAlarms(time)
    if primeAlarms is None:
        return None
    newAlarms = filterAlarms(primeAlarms)
    return newAlarms

def saveNewAlarms(alarms):
    return persist.saveAlarms(alarms)

def sendAlarmsToRemedy(alarms):
    alarmsToSend = []
    for alarm in alarms:
        alarmsToSend.append({
            'title': '{0} - {1}'.format(alarm['alarmsDTO']['condition']['value'], alarm['alarmsDTO']['deviceName']),
            'description': alarm['alarmsDTO']['message']
        })
        ticket = services.postAlarmRemedy(alarmsToSend)
        alarm['ticket'] = ticket
    print('Alarms sended')
    print(alarms)

def getTimeToQuery():
    time = datetime.datetime.now() - datetime.timedelta(seconds=timeToSearchAlarms)
    return time.strftime('%Y-%m-%dT%H:%M:%S')

def __main__():
    print('Captura de alarmas Cisco Prime')
    time = getTimeToQuery()
    print('Mostrando alarmas desde: {0}'.format(time))
    alarms = getNewAlarms(time)
    if not alarms:
        print('No se encontraron alarmas')
    else:
        print(alarms)
        sendAlarmsToRemedy(alarms)
        result = persist.saveAlarms(alarms)
        print(result)
    print('Proceso finalizado')

__main__()