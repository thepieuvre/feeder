import locale
import optparse
import redis
import sys

if sys.hexversion < 0x0240000:
	print >> sys.stderr, 'The python version is too old (%s)' % \
		(sys.version.split()[0])
	print >> sys.stderr, 'At least Python 2.4 is required'
	sys.exit(1)

from feeder.parser import get
from feeder.version import VERSION
from urlparse import urlparse

def parse_cmdline():
	usage = '%s [OPTIONS] RSS Feeds...' % (sys.argv[0])
	parser = optparse.OptionParser(usage, version='The Pieuvre Feeder ' + VERSION)
	parser.add_option('--verbose', action='store_true', dest='verbose',
		help='print verbose information')
	parser.add_option('--id', type='int', dest='id', help='id of the feed')
	parser.add_option('--etag', type='string', dest='etag', help='eTag for cache optimisation')
	parser.add_option('--modified', type='string', dest='modified', help='modified for cache optimisation')
	parser.add_option('--redis-url', type='string', dest='redis_url',
		help='consuming the feeder queue from the local Redis')

	options, args = parser.parse_args()

	if options.redis_url:
		if len(args) > 0: 
			parser.error('No RSS feeds needed when REDIS in use')
	
		redis_host_port = urlparse(options.redis_url).netloc.split(':')
		if (len (redis_host_port) != 2):
			parser.error('Expecting a url for redis, like redis://host.domain.fr:456/')
		options.redis_url = redis_host_port

	elif len(args) == 0:
		parser.error('No RSS feeds given')

	return options, args

def main():
	"""Starting the Pieuvre feeder"""
	locale.setlocale(locale.LC_ALL, '')
	options, args = parse_cmdline()
	if options.redis_url:
		r = redis.StrictRedis(host=redis_url[0], port=int(redis_url[1]), db=0)
		r.sadd('queues', 'feedparser')
		get(None, options.id, options.etag, options.modified, redis=r)
	else:
		for url in args:
			get(url, options.id, options.etag, options.modified)
