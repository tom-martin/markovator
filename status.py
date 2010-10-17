import logging
from django.utils import simplejson as json
from google.appengine.ext import db

class AppStatus(db.Model):
    json_string = db.StringProperty()

def clear():
    app_statuses = AppStatus.all()
    for app_status in app_statuses:
        app_status.delete()

def load_entity():
    app_statuses = AppStatus.all()

    if app_statuses.count() == 0:
        app_status = AppStatus()
        app_status.json_string = "{}"
        app_status.put()
        return app_status

    return app_statuses[0]


def load():
    return json.loads(load_entity().json_string)

def save(app_status):
    current_app_status = load_entity()
    current_app_status.json_string = json.dumps(app_status)
    current_app_status.put()


