import cgi
from django.utils import simplejson as json
import random

import twitter

from google.appengine.ext import webapp
from google.appengine.ext import db

from google.appengine.api import urlfetch


import twitter
import status

class StatusHandler(webapp.RequestHandler):
  def get(self):
    entity = status.load_entity()
    self.response.out.write("<pre>" + entity.json_string +  "</pre>")
    self.response.out.write("<form action='/status/' method='POST'><label for='json_status'>Change</label><textarea name='json_status' rows='2' cols='100'>" + entity.json_string + "</textarea><input type='submit' value='update status'/></form>")

    self.response.out.write("<pre>" + json.dumps(twitter.get_rate_limit_status(True)) + "</pre>");


  def post(self):
    status.save(json.loads(self.request.get("json_status")))
    self.get()

class ClearStatusHandler(webapp.RequestHandler):
  def get(self):
    status.clear()
    self.response.out.write("<p>Cleared</p>")


