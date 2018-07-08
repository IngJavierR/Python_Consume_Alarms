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

def getAlarmsCounter(dateTime):
    db = getConnection()
    doc = db['alarms-counter'].find({'datetime': dateTime})
    return dumps(doc)

def getAllAlarmsCounter():
    db = getConnection()
    doc = db['alarms-counter'].find()
    return dumps(doc)

def saveAlarmCounter(alarms):
    db = getConnection()
    doc = db['alarms-counter'].save(alarms)
    return doc.inserted_ids