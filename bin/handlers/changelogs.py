from flask import Blueprint, render_template, request
from .. import databaseAPI as DBAPI
import json

def displayChangelog():
    userList = DBAPI.obtainUser('_ALL_')
    return render_template('changelog.html', users = userList, mode = request.cookies.get('mode'))

def queryLogs(requestData):
    changelogs = DBAPI.queryLogs( int(requestData.get('adminid')), int(requestData.get('datestart')), int(requestData.get('dateend')) )
    changelog = []
    for log in changelogs:
        changelog.append({'adminid' : log.userid, 'timestamp' : log.timestamp, 'description' : log.description})
    return json.dumps(changelog)