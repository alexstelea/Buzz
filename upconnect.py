""" Places providers which query location services for information about nearby points of interest """
import json
import urllib
import urllib2
import logging

UP_API_OAUTH_HOST = "https://jawbone.com/auth/oauth2"
UP_API_HOST = "https://jawbone.com/nudge/api"

class UPProvider(object):
    
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
    
    def get_connect_url(self, redirect, permissions):
        return "%s/auth?%s" % (
            UP_API_OAUTH_HOST,
            urllib.urlencode({
                    'response_type' : 'code',
                    'client_id' : self._client_id,
                    'scope' : permissions,
                    'redirect_uri' : redirect
                    })
            )

    def _request(self, request):
        """
        _request wraps UP server requests in a try catch block
        print out the details of the error and return the data object
        """
        try:
            content = urllib2.urlopen(request).read()
        except IOError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error: ', e.read()
            raise e
            
        return json.loads(content)

    def get_user_token(self, code):
        url = "%s/token?%s" % (
            UP_API_OAUTH_HOST,
            urllib.urlencode({
                    'code' : code,
                    'client_secret' : self._client_secret,
                    'client_id' : self._client_id,
                    'grant_type' : 'authorization_code'
                    })
            )
        req = urllib2.Request(url)
        response = self._request(req)
        logging.debug(response)
        return response

    def read(self, access_token, method, data={}):
        url = "%s/%s" % (UP_API_HOST, method)
        if data:
            url = "%s?%s" % (url, urllib.urlencode(data))
        req = urllib2.Request(url, None, {'Authorization':'Bearer %s' % access_token})
        response = self._request(req)
        logging.debug(response)
        return response

    def write(self, access_token, method, data={}):
        url = "%s/%s" % (UP_API_HOST, method)
        req = urllib2.Request(url, urllib.urlencode(data), {'Authorization':'Bearer %s' % access_token})
        response = self._request(req)
        logging.debug(response)
        return response
        

    class Workout(object):
        def __init__(self, start, end, type, photo_url):
            self._info = {
                'time_created' : start,
                'time_completed' : end,
                'sub_type' : type,
                'image_url' : photo_url
                }

        def to_post_data(self):
            obj = {}
            obj.update(self._info)
            return obj
            
    def write_workout(self, access_token, workout):
        return self.write(
            access_token,
            'users/@me/workouts',
            workout.to_post_data()
            )

    class Meal(object):
        def __init__(self, photo_url, title):
            self._items = []
            self._info = {
                'sub_type' : 1,
                'image' : photo_url,
                'note' : title
                }
            
        def add_place(self, name, lat, lon, external_id=None):
            """
            we should probably save the external id of the place in the future
            """
            self._info.update({
                    'place_name' : name,
                    'place_lat' : lat,
                    'place_lon' : lon
                    })

        def add_item(self, meal_item):
            self._items.append(meal_item)

        def to_post_data(self):
            obj = {}
            obj.update(self._info)
            obj.update({
                    'items' : json.dumps([ item.to_dict() for item in self._items ])
                    })
            return obj

    class MealItem(object):

        class types(object):
            drink = 1
            food = 2

        def __init__(self, name, description=None, image=None, type='plate', food_type='generic', sub_type=types.food):
            self._info = {
                'name' : name,
                'description' : description,
                'image' : image,
                'type' : type,
                'sub_type' : sub_type,
                'food_type' : food_type
                }

        def add_nutritional_data(self, amount, measurement, nutrients):
            self._info.update({
                    'amount' : amount,
                    'measurement' : measurement,
                    })
            self._info.update(nutrients)

        def to_dict(self):
            d = {}
            d.update(self._info)
            return d

    def write_meal(self, access_token, meal):
        return self.write(
            access_token,
            'users/@me/meals',
            meal.to_post_data()
            )
    


