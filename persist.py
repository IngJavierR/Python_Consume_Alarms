from pymongo import MongoClient
from bson.json_util import dumps

def getConnection():
    client = MongoClient('mongodb://localhost:27017/')
    return client['prime']

def getAllAlarms():
    db = getConnection()
    doc = db['alarms'].find()
    return dumps(doc)

def saveAlarms(alarms):
    db = getConnection()
    doc = db['alarms'].insert_many(alarms)
    return doc.inserted_ids

def getAlarmsCounter(time):
    db = getConnection()
    doc = db['alarmscounter'].find_one({'datetime': time})
    if doc is None:
        return None
    else:
        return doc

def getAllAlarmsCounter(day):
    db = getConnection()
    doc = db['alarmscounter'].find({'originday': day})
    return doc

def saveAlarmCounter(alarms):
    db = getConnection()
    doc = db['alarmscounter'].save(alarms)
    return doc