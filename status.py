from google.appengine.ext import db

class AppStatus(db.Model):
    reply_since_id = db.IntegerProperty()


def get_reply_since_id():
    app_statuses = AppStatus.all()

    if app_statuses.count() == 0:
        AppStatus().put()
        return -1

    return app_statuses[0].reply_since_id

def set_reply_since_id(since_id):
    app_statuses = AppStatus.all()

    if app_statuses.count() == 0:
        app_status = AppStatus()
    else:
        app_status = app_statuses[0]

    app_status.reply_since_id = since_id

    another_app_status = AppStatus()
    another_app_status.reply_since_id = 12

    app_status.put()




