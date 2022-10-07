from flask import render_template, request
from .. import database_api as DBAPI
import json
import sys


def displayChangelog():
    userList = DBAPI.obtainUser('_ALL_')
    return render_template('changelog.html', users=userList, mode=request.cookies.get('mode'))


def queryLogs(requestData):
    adminID = None if int(requestData.get('adminid')) == - \
        1 else int(requestData.get('adminid'))
    dateStart = 0 if int(requestData.get('datestart')) == - \
        1 else int(requestData.get('datestart'))
    dateEnd = sys.maxsize if int(requestData.get(
        'dateend')) == -1 else int(requestData.get('dateend'))

    changelogs = DBAPI.queryLogs(adminID, dateStart, dateEnd)
    changelog = []
    for log in changelogs:
        changelog.append({
            'adminid': log.userid,
            'timestamp': log.timestamp,
            'description': log.description
        })
    return json.dumps(changelog)


def displayValidationLog():
    return render_template('validationlogs.html', mode=request.cookies.get('mode'))


def queryValidationLogs(requestData):
    typeSearch = None if str(requestData.get('typeSearch')) == '' else str(
        requestData.get('typeSearch'))
    dateStart = 0 if int(requestData.get('datestart')) == - \
        1 else int(requestData.get('datestart'))
    dateEnd = sys.maxsize if int(requestData.get(
        'dateend')) == -1 else int(requestData.get('dateend'))

    validationLogs = DBAPI.queryValidationLogs(typeSearch, dateStart, dateEnd)
    responseArray = []
    for log in validationLogs:
        responseArray.append({
            'timestamp': log.timestamp,
            'result': log.result,
            'type': log.type,
            'ipaddress': log.ipaddress,
            'apiKey': log.apiKey,
            'serialKey': log.serialKey,
            'hardwareID': log.hardwareID
        })
    return json.dumps(responseArray)
