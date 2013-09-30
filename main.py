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

class UserModel(ndb.Model):
    """ Models a User """
    tid   = ndb.IntegerProperty()
    xid   = ndb.StringProperty()
    token = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

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

        self.response.write('''
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <link href="/stylesheets/main.css" media="screen" rel="stylesheet" type="text/css"/>
  <link href="/stylesheets/bootstrap.css" rel="stylesheet">
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" ></script>
<script type="text/javascript" src="http://www.google.com/jsapi"></script>

  <script src="/js/lastfm.js"></script>
  <script src="/js/lastfm.api.md5.js"></script>

  <script src="js/raphael.js"></script>
  <script src="js/justgage.1.0.1.min.js"></script>

  <script src="js/popup.js"></script>

  <script>
    


  Raphael.fn.drawGrid = function (x, y, w, h, wv, hv, color) {
            color = "rgba(0,0,0,0.1)";
            var path = ["M", Math.round(x) + .5, Math.round(y) + .5, "L", Math.round(x + w) + .5, Math.round(y) + .5, Math.round(x + w) + .5, Math.round(y + h) + .5, Math.round(x) + .5, Math.round(y + h) + .5, Math.round(x) + .5, Math.round(y) + .5],
                rowHeight = h / hv,
                columnWidth = w / wv;
            for (var i = 1; i < hv; i++) {
                path = path.concat(["M", Math.round(x) + .5, Math.round(y + i * rowHeight) + .5, "H", Math.round(x + w) + .5]);
            }
            for (i = 1; i < wv; i++) {
                path = path.concat(["M", Math.round(x + i * columnWidth) + .5, Math.round(y) + .5, "V", Math.round(y + h) + .5]);
            }
            return this.path(path.join(",")).attr({stroke: color});
        };

        $(function () {
            $("#data").css({
                position: "absolute",
                left: "-9999em",
                top: "-9999em"
            });
        });

        window.onload = function () {
            function getAnchors(p1x, p1y, p2x, p2y, p3x, p3y) {
                var l1 = (p2x - p1x) / 2,
                    l2 = (p3x - p2x) / 2,
                    a = Math.atan((p2x - p1x) / Math.abs(p2y - p1y)),
                    b = Math.atan((p3x - p2x) / Math.abs(p2y - p3y));
                a = p1y < p2y ? Math.PI - a : a;
                b = p3y < p2y ? Math.PI - b : b;
                var alpha = Math.PI / 2 - ((a + b) % (Math.PI * 2)) / 2,
                    dx1 = l1 * Math.sin(alpha + a),
                    dy1 = l1 * Math.cos(alpha + a),
                    dx2 = l2 * Math.sin(alpha + b),
                    dy2 = l2 * Math.cos(alpha + b);
                return {
                    x1: p2x - dx1,
                    y1: p2y + dy1,
                    x2: p2x + dx2,
                    y2: p2y + dy2
                };
            }
            // Grab the data
            var labels = [],
                data = [];
            $("#data tfoot th").each(function () {
                labels.push($(this).html());
            });
            $("#data tbody td").each(function () {
                data.push($(this).html());
            });
            
            // Draw
            var width = $("#holder").width(),
                height = 250,
                leftgutter = 0,
                bottomgutter = 20,
                topgutter = 20,
                colorhue = .6 || Math.random(),
                color = "hsl(" + [colorhue, .5, .5] + ")",
                r = Raphael("holder", width, height),
                txt = {font: '12px Helvetica, Arial', fill: "#000"},
                txt1 = {font: '10px Helvetica, Arial', fill: "#000"},
                txt2 = {font: '12px Helvetica, Arial', fill: "#000"},
                txt3 = {font: '12px Helvetica, Arial', fill: "#fff"},
                X = (width - leftgutter) / labels.length,
                labels3 = r.set(),
                max = Math.max.apply(Math, data),
                Y = (height - bottomgutter - topgutter) / max;
            
            
            r.drawGrid(160, 80, 620, 10, 80, 10, "#fff");
            labels3.push(r.text(80, 85, "Average Stress Score").attr(txt2));

            r.drawGrid(leftgutter + X * .5 + .5, topgutter + .5, width - leftgutter - X, height - topgutter - bottomgutter, 10, 10, "#000");
            var path = r.path().attr({stroke: color, "stroke-width": 4, "stroke-linejoin": "round"}),
                bgp = r.path().attr({stroke: "none", opacity: .3, fill: color}),
                label = r.set(),

                lx = 0, ly = 0,
                is_label_visible = false,
                leave_timer,
                blanket = r.set();
            label.push(r.text(60, 12, "24 hits").attr(txt3));
            label.push(r.text(60, 27, "22 September 2008").attr(txt1).attr({fill: color}));
            label.hide();
            
            var frame = r.popup(100, 100, label, "right").attr({fill: "#000", stroke: "#666", "stroke-width": 2, "fill-opacity": .7}).hide();

            var p, bgpp;
            for (var i = 0, ii = labels.length; i < ii; i++) {
                var y = Math.round(height - bottomgutter - Y * data[i]),
                    x = Math.round(leftgutter + X * (i + .5)),
                    t = r.text(x, height - 6, labels[i]).attr(txt).toBack();
                if (!i) {
                    p = ["M", x, y, "C", x, y];
                    bgpp = ["M", leftgutter + X * .5, height - bottomgutter, "L", x, y, "C", x, y];
                }
                if (i && i < ii - 1) {
                    var Y0 = Math.round(height - bottomgutter - Y * data[i - 1]),
                        X0 = Math.round(leftgutter + X * (i - .5)),
                        Y2 = Math.round(height - bottomgutter - Y * data[i + 1]),
                        X2 = Math.round(leftgutter + X * (i + 1.5));
                    var a = getAnchors(X0, Y0, x, y, X2, Y2);
                    p = p.concat([a.x1, a.y1, x, y, a.x2, a.y2]);
                    bgpp = bgpp.concat([a.x1, a.y1, x, y, a.x2, a.y2]);
                }
                var dot = r.circle(x, y, 4).attr({fill: "#333", stroke: color, "stroke-width": 2});
                blanket.push(r.rect(leftgutter + X * i, 0, X, height - bottomgutter).attr({stroke: "none", fill: "#fff", opacity: 0}));
                var rect = blanket[blanket.length - 1];
                (function (x, y, data, lbl, dot) {
                    var timer, i = 0;
                    rect.hover(function () {
                        clearTimeout(leave_timer);
                        var side = "right";
                        if (x + frame.getBBox().width > width) {
                            side = "left";
                        }
                        var ppp = r.popup(x, y, label, side, 1),
                            anim = Raphael.animation({
                                path: ppp.path,
                                transform: ["t", ppp.dx, ppp.dy]
                            }, 200 * is_label_visible);
                        lx = label[0].transform()[0][1] + ppp.dx;
                        ly = label[0].transform()[0][2] + ppp.dy;
                        frame.show().stop().animate(anim);
                        label[0].attr({text: "Total Stress " + data + " "}).show().stop().animateWith(frame, anim, {transform: ["t", lx, ly]}, 200 * is_label_visible);
                        label[1].attr({text: lbl}).show().stop().animateWith(frame, anim, {transform: ["t", lx, ly]}, 200 * is_label_visible);
                        dot.attr("r", 6);
                        is_label_visible = true;
                    }, function () {
                        dot.attr("r", 4);
                        leave_timer = setTimeout(function () {
                            frame.hide();
                            label[0].hide();
                            label[1].hide();
                            is_label_visible = false;
                        }, 1);
                    });
                })(x, y, data[i], labels[i], dot);
            }
            p = p.concat([x, y, x, y]);
            bgpp = bgpp.concat([x, y, x, y, "L", x, height - bottomgutter, "z"]);
            path.attr({path: p});
            bgp.attr({path: bgpp});
            frame.toFront();
            label[0].toFront();
            label[1].toFront();
            blanket.toFront();
        };

</script>
 <style type="text/css">

rect.a {
        fill: green;
      }
      rect.b {
        fill: orange;
      }
      rect.c {
        fill: red;
      }


    </style>
</head>

<body>

<div class="navbar navbar-inverse">
  <div class="navbar-inner">
    <a class="brand" href="#">Buzz</a>
    <ul class="nav">
      <li class="active"><a href="#">Home</a></li>
      <li><a href="/connect">Login</a></li>
      <li><a href="/signout">Logout</a></li>
    </ul>
  </div>
</div>
<div class="container">


  <div class="table well span12">
    <div id="gauge" style="display: block; margin: 0 auto; width:400px; height:320px"></div>
    <div style="width: 600px; margin-top: 50px;  margin: 0 auto; height: 200px;">
      <div id="sleep-gauge" style="position: relative; float: left;width:200px; height:160px"></div> 
      <div id="activity-gauge" style="position: relative; float: left; width:200px; height:160px"></div> 
      <div id="calendar-gauge" style="position: relative; float: left; width:200px; height:160px"></div>
    </div>
  </div>

  <div class="row">
    <div class="span6" style="margin-left: 40px;"">
    <h4>Your Daily Event Stress Score:</h4>
      <ul>
        <li>Exams: <strong>(3)</strong> scheduled today from 2PM - 5PM</li>
        <li>Meetings: <strong>(2)</strong> group Meetings today from 6PM - 8PM</li>
        <li>Classes: <strong>(5)</strong> classes today from 10AM - 4PM</li>
      </ul>
    </div>
    <div class="span5">
    <h4>Your Music Score:</h4>
      <p>Hi Alex Stelea, you listened to your usual song types.</p>
      <p>Based on your browse history, here is some recommended music to help you unwind:</p>
      <ul>
        <li><a href="#">That's My Name</a> - Akcent</li>
        <li><a href="#">I Feel Better</a> - Hot Chip</li>
        <li><a href="#">Mirros</a> - Justin Timberlake</li>

      </ul>
    </div>
  </div>

  <div class="span12">

  </div>

  <div class="graph-container">
    <table id="data">
                <h4 style="margin-bottom: 0px; margin-top: 70px;" align="center">Historic Stress Diagram</h4>    
                    <tfoot>
                        <tr>
                            <th>9/27/2013</th>
                            <th>9/28/2013</th>
                            <th>9/29/2013</th>
                        </tr>
                    </tfoot>
                    <tbody>
                        <tr>
                            <td>75.06</td>
                            <td>50.76</td>
                            <td>81.71</td>
                        </tr>
                    </tbody>
                </table>   

                <div id="holder"></div>
                </div>
</div>


<div style="margin-top: 60px"></div>
</body>


<script type="text/javascript">

           
 
var max = 0;

move_score = function(data) {
  if (data['move_cnt'] == 0) {
    return 0;
  }
  return (data['steps']/data['move_cnt']/100).toFixed(0);
}

sleep_score = function(data) {


  return (data['sleep_main']['quality'] - Math.pow(data['sleep_main']['awakenings'],3)).toFixed(0);

}

final_score = function(data){
  return ((calendar_score(data) + move_score(data) + sleep_score(data))/14000).toFixed(0);
}

calendar_score = function(data){
  return (85-(sleep_score(data)/10) + (move_score(data)/10)).toFixed(0);
}




fetch_team = function(tid) {

$.get('/teamscore?tid='+tid, function(data) {

  
  var g = new JustGage({
    id: "gauge", 
    value: final_score(data), 
    min: 0,
    max: 100,
    title: "Stress Score"
  }); 


  var g = new JustGage({
      id: "sleep-gauge", 
      value: sleep_score(data), 
      min: 0,
      max: 100,
      title: "Sleep Score"
    });  
  var g = new JustGage({
      id: "activity-gauge", 
      value: move_score(data), 
      min: 0,
      max: 100,
      title: "Activity Score"
    });  
  var g = new JustGage({
      id: "calendar-gauge", 
      value: calendar_score(data), 
      min: 0,
      max: 100,
      title: "Schedule Score"
    });  

});

}


$(document).ready(function() {
  
  fetch_team('XkPN_Wb3hGwgc7ZHX4ErSQ');
  

});




</script>

</html>
''' 
)

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

        # Misha Wrote This part lolollol

        up_sleep = up.read(token, 'users/@me/sleeps')


        month_sleep =[]

        for line in up_sleep['data']['items']:
          month_sleep.append((line['details']['light'] * 1.5/line['details']['duration']) * 100)


        # while len(month_sleep)<=30:
        #   if len(month_sleep) != 30:
        #     month_sleep = month_sleep.append(up_time_completed)
        #     average_sleep = sum(month_sleep)/ len(month_sleep)
        #     print("hiii")
        #     print(average_sleep)
        #   else:
        #     month_sleep = month_sleep[1:]
        #     month_sleep = month_sleep.append(up_time_completed)
        #     print("your average sleep is", average_sleep)

        
        # mean = sum(mouth_sleep, 0.0) / len(scorenum)
        # d = [ (i - mean) ** 2 for i in scorenum]
        # std_dev = math.sqrt(sum(d) / len(d))

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


class ConnectLastFM(MainHandler):
  def get(self):
    pass

class ConnectHandler(MainHandler):

    def get(self):
        up = self._up_provider()
        redirect = '%s/authorize' % self.request.host_url
        url = up.get_connect_url(redirect, 'basic_read extended_read move_read sleep_read meal_read')

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('''
<html>
<head>
  <link href="/stylesheets/main.css" media="screen" rel="stylesheet" type="text/css"/>
  <link href="/stylesheets/bootstrap.css" rel="stylesheet">
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" ></script>
  <style type="text/css">
      body {
        padding-top: 40px;
        padding-bottom: 40px;
        background-color: #f5f5f5;
      }

      .form-signin {
        max-width: 300px;
        padding: 19px 29px 29px;
        margin: 0 auto 20px;
        background-color: #fff;
        border: 1px solid #e5e5e5;
        -webkit-border-radius: 5px;
           -moz-border-radius: 5px;
                border-radius: 5px;
        -webkit-box-shadow: 0 1px 2px rgba(0,0,0,.05);
           -moz-box-shadow: 0 1px 2px rgba(0,0,0,.05);
                box-shadow: 0 1px 2px rgba(0,0,0,.05);
      }
      .form-signin .form-signin-heading,
      .form-signin .checkbox {
        margin-bottom: 10px;
      }
      .form-signin input[type="text"],
      .form-signin input[type="password"] {
        font-size: 16px;
        height: auto;
        margin-bottom: 15px;
        padding: 7px 9px;
      }

    </style>
</head>


<div class="container">

      <form action="" class="form-signin">
        <h2 style="text-align: center">Welcome to Buzz</h3>

        <h5 style="text-align: center">Connect to Jawbone</h5>
        <button style="margin-left: 110px;" class="btn btn-large btn-primary" type="submit"><a style="color: white" href="%s">Login</a></button>
        
      </form>
    </div>

</html>
''' % url)
        

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
        self.redirect('/team')



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/connect', ConnectHandler),
    ('/authorize', AuthorizeHandler),
    ('/team', TeamHandler),
    ('/teamchoose', TeamChooseHandler),
    ('/teamscore', TeamScoreHandler),
    ('/signout', SignoutHandler)
], debug=True)
