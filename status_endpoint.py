import cgi
from django.utils import simplejson as json
import random

from google.appengine.ext import webapp
from google.appengine.ext import db

from google.appengine.api import urlfetch

import twitter
import status

class StatusHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write("<p>Reply since id: " + str(status.get_reply_since_id()) + "</p>")
    self.response.out.write("<form action='/status/' method='POST'><label for='since_id'>Change <input type='text' name='since_id'></input></form>")


  def post(self):
    status.set_reply_since_id(int(self.request.get("since_id")))
    self.get()


