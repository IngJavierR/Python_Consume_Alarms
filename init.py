import persist
import services
import datetime
import schedule
import time

#Fine Alarms Every (minutes)
timeToSearchAlarms = 1

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
            'description': alarm['alarmsDTO']['message'],
            'affectedClient': 'BMC',
            'impact': '4-Menor/Localizado',
            'severity': '4-Baja'
        })
        ticket = services.postAlarmRemedy(alarmsToSend)
        alarm['ticket'] = ticket
    print('Alarms sended')

def getTimeToQuery():
    time = datetime.datetime.now() - datetime.timedelta(minutes=timeToSearchAlarms)
    return time.strftime('%Y-%m-%dT%H:%M:%S')

def job():
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
    print('Finalizado, nueva ejecucion en: {0} minutos'.format(timeToSearchAlarms))

def __main__():
    job()
    schedule.every(timeToSearchAlarms).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

__main__()