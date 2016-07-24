#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import time

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import SurviveAPI
from utils import get_by_urlsafe

from models import User, Game


class SendNewGameEmail(webapp2.RequestHandler):
    def post(self):
        """Send email to user once creating a new game"""
        subject = 'Thank you for playing survivor'
        body = 'Hello {} you have a new game in progress. Enjoy!'.format\
        (self.request.get('name'))
        # This will send test emails, the arguments to send_mail are:
        # from, to, subject, body
        mail.send_mail('noreply@{}.appspotmail.com'.format \
          (app_identity.get_application_id()),
          self.request.get('email'),
          subject,
          body)


class ReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to players with an aging game"""
        #querygame = Game.query()
        #querygame = querygame.filter(Game.game_over==False).get()
        #timecompare= int(time.time())
        users = User.query(User.email != None)

        for user in users:
            games =Game.query(Game.user == user.key).filter(Game.game_over == False)
            if games.count() > 0:
                sender = 'noreply@{}.appspotmail.com'.format(app_identity.get_application_id())
                to = user.email
                subject = 'Hello {}, play your game dude!'.format(user.name)
                body = "Dude, it is time to finish this!!!!!" 
                mail.send_mail(sender, to, subject, body) 
                    
               


 # I need to query the user ndb to get emails for the games users that have an active game.




app = webapp2.WSGIApplication([
    ('/tasks/send_newgame_email', SendNewGameEmail), ('/cron/send_reminder',\
     ReminderEmail)], debug=True)
