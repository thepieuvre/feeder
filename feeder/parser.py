import feedparser
import json
import logging
import sys
import traceback
import time

AGENT='Feeder-ThePieuvre; (+http://www.thepieuvre.com; %s subscribers; feed-id=%s)'

REFERRER='http://www.thepieuvre.com'

DATE_FORMAT="%Y-%m-%d %H:%M:%S %Z"

log = logging.getLogger(__name__)

def escaping(str):
	return str.replace('\\','\\\\').replace('"','\\"')

def processing_task(task):
	feed = json.loads(task)
	return process_url(feed['link'], feed['eTag'], feed['modified'], feed['id'], feed['subscribers'])

def redis_mode(redis):
	while True:
		try:
			task = redis.blpop('queue:feeder', 10)
			if task != None:
				log.info('Getting: %s'%(task[1]))
				redis.rpush('queue:feedparser',processing_task(task[1]))
				log.info('Pushed to queue:feedparser')
		except KeyboardInterrupt:
			sys.exit(0)
		except:
			traceback.print_exc()

def get(url, id, etag, modified, redis=None):
	if redis != None:
		redis_mode(redis)
	else:
		print process_url(url, etag, modified)

from HttpHelpers import is_html, get_feed_url
from urllib2 import HTTPError, URLError, socket

def error_json(error='null', status='null') :
   ''' Creates a JSON for error treatment '''
   current_date = time.strftime(DATE_FORMAT).encode('utf-8')
   json = '''{
    "description": "null", 
    "etag": "null", 
    "language": "null", 
    "modified": "%s", 
    "standard": "null", 
    "status": "%s", 
    "title": "null", 
    "updated": "%s", 
    "error": "%s"
}''' % (current_date, status, current_date, error)
   return json

def process_url(link, etag, modified, id=None, subscribers=0):
   try: 
      #if is_html(link):
      #   link = get_feed_url (link)
      log.debug('Processing URL - %s'%(link))
      data = feedparser.parse(link, etag=etag, modified=modified, agent=AGENT%(subscribers, id), referrer=REFERRER)
      log.debug('Processed - %s'%(data.feed.get('title', 'null')))
      return process_data(data, id)
   except HTTPError as err:
      if hasattr(err, 'reason'):
         return error_json(err.reason, err.code)
      else:
      	 return error_json('no reason', err.code)
   except URLError as err:
      if isinstance(err.reason, socket.error):
         msg = err.reason[1]
      else:
         msg = err.reason
      return error_json(msg)

def as_date(feed_key, parsed_feed):
   '''helper method: retrieve a date field from a parsed feed'''
   date = parsed_feed.get(feed_key + '_parsed')
   if (date == None):
      return 'null'   
   else:
      return time.strftime(DATE_FORMAT, date).encode('utf-8')

def process_data(data, id):
	str_list = []	
	str_list.append('{')
	if id != None:
		str_list.append(('"id": "%s",'% id))
	str_list.append(('"title": "%s",'% escaping((data.feed.get('title', 'null'))).encode('utf-8')))
	str_list.append(('"uuid": "%s",'% escaping((data.feed.get('id', 'null'))).encode('utf-8')))
	str_list.append(('"description": "%s",'% escaping((data.feed.get('description', 'null'))).encode('utf-8')))
	str_list.append(('"language": "%s",'% escaping((data.feed.get('language', 'en'))).encode('utf-8')))
	str_list.append(('"status": "%s",'% (data.get('status', '-1'))).encode('utf-8'))
	str_list.append(('"standard": "%s",'% escaping((data.get('version','null'))).encode('utf-8')))
	str_list.append(('"etag": "%s",'% escaping((data.get('etag', 'null')).replace('"','')).encode('utf-8')))
	str_list.append(('"modified": "%s",' % as_date('modified', data))) 
	status = data.get('status', -1)
	if status == 301:
		str_list.append(('"moved": "%s",' % escaping((data.href)).encode('utf-8')))
	str_list.append(('"updated": "%s",'% as_date('modified', data)))
	str_list.append('"articles": ['.encode('utf-8'))
	size = len(data.entries)
	counter = 0
	for article in data.entries:
		counter = counter + 1
		str_list.append(('{ "title": "%s",' % escaping(article.get('title', 'null')).encode('utf-8')))
		str_list.append(('"link": "%s",' % escaping((article.get('link', 'null').encode('utf-8')))))
		str_list.append(('"author": "%s",' % escaping((article.get('author', 'null').encode('utf-8')))))
		str_list.append('"contents": [')
		if article.get('content'):
			contentSize = len(article.content)
			contentCounter = 0
			for content in article.content:
				contentCounter = contentCounter + 1
				str_list.append('"%s"' %escaping(content.get('value', 'null').encode('utf-8')))
				if contentCounter != contentSize:
					str_list.append(',')
		elif article.get('summary_detail'):
			str_list.append('"%s"' %escaping(article.summary_detail.get('value', 'null').encode('utf-8')))
		str_list.append('],')
		str_list.append(('"published": "%s",' % as_date('published', article)))
		str_list.append(('"id": "%s" }' % escaping((article.get('id', 'null'))).encode('utf-8')))
		if counter != size:
			str_list.append(",")
	str_list.append(']')
	str_list.append('}')
	return ''.join(str_list).replace('\n',' ')
	
