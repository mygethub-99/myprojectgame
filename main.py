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

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import SurviveAPI
from utils import get_by_urlsafe

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send email to user once creating a new game"""

        subject = 'Thank you for playing survivor'
        body = 'Hello {} you have a new game in progress. Enjoy!'.format(self.request.get('name'))
        # This will send test emails, the arguments to send_mail are:
        # from, to, subject, body
        x = self.request.get('email')
        print x
        mail.send_mail('noreply@{}.appspotmail.com'.format \
          (app_identity.get_application_id()),
          self.request.get('email'),
          subject,
          body)


app = webapp2.WSGIApplication([
    ('/tasks/send_newgame_email', SendReminderEmail)], debug=True)
