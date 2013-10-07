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
import webapp2
import upconnect
import cgi
import logging
import json

from google.appengine.ext import ndb

# tools for encryption
app_name = "Buzz"

# your keys go here

app_config = {
    'UP_API_CLIENT_ID': "krS_McZKM9M",
    'UP_API_SECRET': "48e15085df4a81f292ebef0a33bf91deb0bb4d6f",
}

class CalendarModel(ndb.Model):
  cid = ndb.IntegerProperty()
  name = ndb.StringProperty()
  pass


class StressModel(ndb.Model):
  """ Stress Model """
  sid = ndb.IntegerProperty()
  score = ndb.IntegerProperty()
  activity = ndb.IntegerProperty()
  sleep = ndb.IntegerProperty()
  calendar = ndb.IntegerProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

    
class UserModel(ndb.Model):
  """ Models a User """
  tid   = ndb.IntegerProperty()
  xid   = ndb.StringProperty()
  token = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)
  stress = ndb.StructuredProperty(StressModel, repeated=True)

  @classmethod
  def query_score(cls, avg_stress_score):
    return UserModel.query(UserModel.avg_stress_score == avg_stress_score).order(-UserModel.data)

  @classmethod
  def query_team(cls, tid):
      return UserModel.query(UserModel.tid == tid).order(-UserModel.date)

  @classmethod
  def query_token(cls, token):
      return UserModel.query(UserModel.token == token).order(-UserModel.date)

  @classmethod
  def query_xid(cls, xid):
      return UserModel.query(UserModel.xid == xid).order(-UserModel.date)


class MainHandler(webapp2.RequestHandler):
  def _up_provider(self):
      return upconnect.UPProvider(app_config['UP_API_CLIENT_ID'], app_config['UP_API_SECRET'])

  def _token(self):
      token = self.request.cookies.get('token', None)
      return token

  def _user(self, xid=None):
    if (xid):
        users = UserModel.query_xid(xid).fetch(1)
    else:
        token = self._token()
        users = UserModel.query_token(token).fetch(1)
    
    if users and users[0]:
        return users[0]
    
    return None

  def _myhost(self):
    return self.request

  def get(self):

    self.response.headers['Content-Type'] = 'text/html'
    with open('main.html','r') as f:
      output = f.read()
    self.response.write(output)

class TeamScoreHandler(MainHandler):
  def _build_team(self, tid):
    up = self._up_provider()
    user = UserModel.query_xid(tid).fetch()

    token = self._token()
    if not token:
        self.redirect('/connect')
        return

    move_cnt = 0
    steps_total = 0
    sleeps_total = 0
    sleep_main = 0;
    try:
      up_sleep = up.read(token, 'users/@me/sleeps')
      sleeps_total = up_sleep['data']['items'][0]['details']['duration']
      sleep_main = up_sleep['data']['items'][0]['details']

    except:
      logging.error('could not fetch sleep for user %s' % user)
    
    try:
      up_moves = up.read(token, 'users/@me/moves')
      for move in up_moves['data']['items']:
          move_cnt += 1
          steps_total += move['details']['steps']
    except:
      logging.error('could not fetch moves for user %s' % user)

    return {
      'team' : tid,
      'move_cnt' : move_cnt,
      'steps' : steps_total,
      'sleep' : sleeps_total,
      'sleep_main' : sleep_main,
      }

  def get(self):
      tid = (cgi.escape(self.request.get('tid')))        
      self.response.headers['Content-Type'] = 'text/json'
      self.response.write(json.dumps(self._build_team(tid)))


class TeamHandler(MainHandler):
  def get(self):
      # 1. make sure the user is logged in
      token = self._token()
      if not token:
          self.redirect('/connect')
          return

      # 2. read user data from the UP API
      up = self._up_provider()
      up_user = up.read(token, 'users/@me')

      up_moves = up.read(token, 'users/@me/moves')

      up_sleep = up.read(token, 'users/@me/sleeps')


      month_sleep =[]

      for line in up_sleep['data']['items']:
        month_sleep.append((line['details']['light'] * 1.5/line['details']['duration']) * 100)

      self.response.headers['Content-Type'] = 'text/html'
      self.response.write('''
<html>
<head>
<link href="/stylesheets/main.css" media="screen" rel="stylesheet" type="text/css"/>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" ></script>
</head>

<div class="canvas">

<b>Hi {first_name}, here is your data</b>
<br/>
{dob}
<br>
<br >
{moves}
<br>
<br>
{len}
<br>
{moth}

<a href="/signout">signout</a>

<p>
{first_name}
</form>
</div>
</html>
'''.format(first_name= up_user['data']['first'], dob=up_user['data'], len = len(up_sleep), moth=month_sleep, moves = up_sleep
))

class TeamChooseHandler(MainHandler):
    
    def post(self):
        up = self._up_provider()
        team = int(self.request.get('team'))

        token = self._token();

        if not token:
            self.redirect('/connect')
            return

        user = self._user()

        if user:
            user.tid = team
        else:
            user = UserModel(tid=team,
                             token=token)

        
        key = user.put()
        ndb.get_context().clear_cache()
        entity = key.get()
        
        self.redirect('/')
        return


class ConnectHandler(MainHandler):

    def get(self):
        up = self._up_provider()
        redirect = '%s/authorize' % self.request.host_url
        url = up.get_connect_url(redirect, 'basic_read extended_read move_read sleep_read meal_read')

        self.response.headers['Content-Type'] = 'text/html'
        with open('login.html','r') as f:
          output = f.read() % url
        self.response.write(output)
        

class AuthorizeHandler(MainHandler):

    def get(self):
        up = self._up_provider()
        code = cgi.escape(self.request.get('code'))
        token = up.get_user_token(code)
        ct = str(token['access_token'])

        # read out the user information and create a user
        up_user = up.read(ct, 'users/@me')
        xid = up_user['data']['xid']
        user = self._user(xid=xid)

        if user:
            user.token = ct
        else:
          user = UserModel(xid=xid,
                             token=ct)
        key = user.put()
        ndb.get_context().clear_cache()
        entity = key.get()
        
        self.response.headers.add_header('Set-Cookie', 'token=%s' % ct)
        self.redirect('/')

class SignoutHandler(MainHandler):

    def get(self):

        self.response.headers.add_header('Set-Cookie', 'token=')
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/connect', ConnectHandler),
    ('/authorize', AuthorizeHandler),
    ('/team', TeamHandler),
    ('/teamchoose', TeamChooseHandler),
    ('/teamscore', TeamScoreHandler),
    ('/signout', SignoutHandler)
], debug=True)
