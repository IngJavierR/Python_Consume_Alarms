import persist, services
import datetime, schedule, time, re

def filterAlarms(alarms):
    print(alarms)
    print('Filter')
    filteredAlarms = list(filter(lambda x: (
        #x['alarmsDTO']['condition']['value'] != 'LINK_DOWN' and
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
    for alarm in alarms:
        alarmToSend = {
            'title': '{0} - {1}'.format(alarm['alarmsDTO']['condition']['value'], alarm['alarmsDTO']['deviceName']),
            'description': alarm['alarmsDTO']['message'],
            'affectedClient': 'BMC',
            'impact': '4-Menor/Localizado',
            'severity': '4-Baja'
        }
        ticket = services.postAlarmRemedy(alarmToSend)
        alarm['ticket'] = ticket
    print('Alarms sended')

def getTimeToQuery(timeToSearchAlarms):
    time = datetime.datetime.now() - datetime.timedelta(minutes=timeToSearchAlarms)
    return time.strftime('%Y-%m-%dT%H:%M:%S')

def getTimeToCounter(hour):
    time = datetime.datetime.now()
    return time.strftime('%Y-%m-%dT%{0}:'.format(hour))

def createAlarmCounter(alarms):
    regex = r"(\d{4}-\d{2}-\d{2}\w\d+)"
    for alarm in alarms:
        resultReg = re.search(regex, alarm['alarmsDTO']['alarmFoundAt'], re.IGNORECASE)
        alarm['alarmsDTO']['dateTime'] = resultReg.group(1)

    alarmsPerHour = []
    for hour in range(0,24):
        alarmsNum = list(filter(lambda x: (
            x['alarmsDTO']['dateTime'].startswith(getTimeToCounter(hour))
        ), alarms))
        alarmsPerHour.append({
            "count": alarmsNum.count(),
            "datetime": getTimeToCounter(hour)
        })
    return alarmsPerHour

def updateAlarmsCounter(alarms):
    alarmsPerHour = createAlarmCounter(alarms)
    for alarms in alarmsPerHour:
        savedAlarm = persist.getAlarmsCounter(alarms[datetime])
        savedAlarm['count'] = savedAlarm['count'] + alarms['count']
        persist.saveAlarmCounter(savedAlarm)

def job(timeToSearchAlarms):
    print('Captura de alarmas Cisco Prime')
    time = getTimeToQuery(timeToSearchAlarms)
    print('Mostrando alarmas desde: {0}'.format(time))
    alarms = getNewAlarms(time)
    if not alarms:
        print('No se encontraron alarmas')
    else:
        print(alarms)
        sendAlarmsToRemedy(alarms)
        updateAlarmsCounter(alarms)
        result = persist.saveAlarms(alarms)
        print(result)
    print('Finalizado, nueva ejecucion en: {0} minutos'.format(timeToSearchAlarms))
    return alarms

def start(timeToSearchAlarms):
    job(timeToSearchAlarms)
    schedule.every(timeToSearchAlarms).minutes.do(job(timeToSearchAlarms))
    while True:
        schedule.run_pending()
        time.sleep(1)