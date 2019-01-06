FACEBOOK_APP_ID = "308826791685"
FACEBOOK_APP_SECRET = "5fb1a19075279dc359e65380480c9565"

import cgi
import datetime
import dateutil.parser
import facebook
import os.path
import time
import urllib
import urllib2

from datetime import date

# Try importing
try:
	import simplejson as json
except ImportError:
	try:
		from django.utils import simplejson as json
	except ImportError:
		import json

# Try importing a query string parser
try:
	from urlparse import parse_qs
except ImportError:
	from cgi import parse_qs


# Get access_token as HelloWorld! facebook app.
def get_access_token():
	response=urllib.urlopen("https://graph.facebook.com/oauth/access_token?" +
							"client_id=308826791685&" +
							"client_secret=5fb1a19075279dc359e65380480c9565&" +
							"grant_type=client_credentials").read()
	query_str = parse_qs(response)
	if "access_token" in query_str:
		return query_str["access_token"][0]
	else:
		response = json.loads(response)
		raise GraphAPIError(response)

def get_posts(_obj_name, _fql, _until, _limit):
	_tries = 1
	while True:
		try:
			token = get_access_token()
			print token
			_graph = facebook.GraphAPI(token)
			_obj = _graph.get_object(_obj_name, fields="id")
			print _fql.format(_obj['id'], _until, _limit)
			_links = _graph.fql(_fql.format(_obj['id'], _until, _limit))
			return _links
		except Exception as e:#urllib2.HTTPError as e:
			print e
			time.sleep(2 * _tries)
			_tries += 1

		if _tries >= 20:
			break;
	#print unicode(_links['data'][0]['message'])
	#return json.dumps(_links['data'], sort_keys=True, indent=2)
	#_link_list = [_link['link'] for _link in _links['data']]
	#print _link_list

def write(_dir, _file, _data):
	f = open(os.path.join("data/fb_crawl/", _dir, str(_file) + ".json"), 'w')
	f.write(json.dumps(_data, sort_keys=True, indent=2))
	f.close()

def crawl(_obj_name, _limit = 500, _cnt = 1, _until = "strtotime('2013-01-01')", _max_date = "2012-09-30T23:59:59"):
    """Crawl Facebook pages for attachments

    :param _obj_name: the Facebook page name
    :param _limit: the max number of links to download per request
    :param _cnt: the current request number
    :param _until: for this request, only fetch attachments before this date
    :param _max_date: downloading is stopped if we hit an article published
    before this date.
    """
    _fql = 'SELECT attachment, created_time FROM stream WHERE source_id = {0} AND created_time < {1} AND type=80 LIMIT {2}'
	# Articles published earlier than _max_date this will not be retrieved.
    _max_date = dateutil.parser.parse(_max_date)
    _tot = 0
    while True:
        _result = get_posts(_obj_name, _fql, _until, _limit)
        write(_obj_name, _cnt, _result)
        _cnt += 1
        _tot += len(_result)
        _until = _result[len(_result) - 1]['created_time']
        _earliest_date = datetime.datetime.fromtimestamp(_until)
        print _earliest_date
        if _earliest_date <= _max_date:
            break;

        print _tot

def main():
    #_newspapers = [ "ElWatanNews", "El.Dostor.News", "almasryalyoum", "aldostornews", "akhbarelyomgate" ]
    _newspapers = [ "bbcarabicnews" ]
    for _it in _newspapers[-1:]:
        cnt = 1
        until = "strtotime('2013-01-01')"
        crawl(_it, _limit=500, _cnt=cnt, _until=until, _max_date="2012-09-30T23:59:59")

if __name__ == "__main__":
	main()
