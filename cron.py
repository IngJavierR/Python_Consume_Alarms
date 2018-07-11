import persist, services
import datetime, schedule, time, re
timeToSearchAlarms = 5
def filterAlarms(alarms):
    print(alarms)
    print('Filter')
    filteredAlarms = list(filter(lambda x: (
        #x['alarmsDTO']['condition']['value'] != 'LINK_DOWN' and
        x['alarmsDTO']['severity'] == 'CRITICAL' or 
        x['alarmsDTO']['severity'] == 'CLEARED'
    ), alarms))
    return filteredAlarms

def getAlarmsNeedTicket(alarms){
    criticalAlarms = list(filter(lambda x: (
        x['alarmsDTO']['severity'] == 'CRITICAL'
    ), alarms))
    return criticalAlarms
}

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
    formatString = '%Y-%m-%dT0{0}' if len(str(hour)) == 1 else '%Y-%m-%dT{0}'
    return time.strftime(formatString.format(hour))

def getDayToCounter():
    time = datetime.datetime.now()
    return time.strftime('%Y-%m-%dT')

def getHourToCounter(hour):
    hourStr = ''
    if hour > 0 and hour < 12:
        hourStr = '{0}am'.format(hour)
    elif hour > 12:
        hourStr = '{0}pm'.format(hour - 12)
    elif hour == 0:
        hourStr = '12am'
    elif hour == 12:
        hourStr = '12pm'
    return hourStr

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
            "counter": len(alarmsNum) if alarmsNum else 0,
            "datetime": getTimeToCounter(hour),
            "hour": getHourToCounter(hour),
            "originday": getDayToCounter()
        })
    return alarmsPerHour

def updateAlarmsCounter(alarms):
    alarmsPerHour = createAlarmCounter(alarms)
    for alarms in alarmsPerHour:
        savedAlarm = persist.getAlarmsCounter(alarms['datetime'])
        if savedAlarm is not None:
            savedAlarm['counter'] = savedAlarm['counter'] + alarms['counter']
        else:
            savedAlarm = {}
            savedAlarm['counter'] = alarms['counter']
            savedAlarm['datetime'] = alarms['datetime']
            savedAlarm['hour'] = alarms['hour']
            savedAlarm['originday'] = alarms['originday']
        persist.saveAlarmCounter(savedAlarm)

def job():
    print('Captura de alarmas Cisco Prime')
    time = getTimeToQuery(timeToSearchAlarms)
    print('Mostrando alarmas desde: {0}'.format(time))
    alarms = getNewAlarms(time)
    alarmsNeedTicket = getAlarmsNeedTicket(alarms)
    if not alarmsNeedTicket:
        alarmsNeedTicket=[]
        print('No se encontraron alarmas')
    else:
        print('Alarms need ticket')
        print(alarmsNeedTicket)
        sendAlarmsToRemedy(alarmsNeedTicket)
        updateAlarmsCounter(alarmsNeedTicket)
        result = persist.saveAlarms(alarmsNeedTicket)
        print(result)
    print('Finalizado, nueva ejecucion en: {0} minutos'.format(timeToSearchAlarms))

def alarms(timeToSearchAlarms):
    print('Captura de alarmas Cisco Prime')
    time = getTimeToQuery(timeToSearchAlarms)
    print('Mostrando alarmas desde: {0}'.format(time))
    alarms = getNewAlarms(time)
    if not alarms:
        alarms=[]
        print('No se encontraron alarmas')
    print(alarms)
    return alarms

def start(cronTime):
    global timeToSearchAlarms
    timeToSearchAlarms = cronTime
    job()