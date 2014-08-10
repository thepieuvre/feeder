import locale
import logging
import logging.config
import optparse
import redis
import socket
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
	parser.add_option('--redis-host', type='string', dest='redis_host',
		help='consuming the feeder queue from the local Redis (host)')
	parser.add_option('--redis-port', type='int', dest='redis_port',
		help='consuming the feeder queue from the local Redis (port)')
	parser.add_option('--logging-config', type='string', dest='logging_config',
		help='Logging configuration path')

	options, args = parser.parse_args()

    # convert redis url in host/port
	if options.redis_url:
		if options.redis_host or options.redis_port:
			parser.error('Redis url incompatible with redis host/port')
		netloc = urlparse(options.redis_url).netloc
		if not netloc:
			parser.error('Redis url is malformed: host/port='+netloc)
		redis_host_port = netloc.split(':')
		if len (redis_host_port) != 2:
			for z in redis_host_port:
				print "arg=" + z
			for n in urlparse(options.redis_url):
				print 'part ' + n 
			print 'base=' + options.redis_url
			parser.error('Expecting a url for redis, like redis://host.domain.fr:456/')
		options.redis_host = redis_host_port[0]
		options.redis_port = redis_host_port[1]

	if options.redis_host:
		if len(args) > 0: 
			parser.error('No RSS feeds needed when REDIS in use')
		if not options.redis_port:
			parser.error('Please specify Redis port: --redis-port=456')
	else:
		if options.redis_port:
			parser.error('Please specify Redis host: --redis-host=server.domain.fr')
		if len(args) == 0:
			parser.error('No RSS feeds given')

	return options, args

def main():
	"""Starting the Pieuvre feeder"""
	locale.setlocale(locale.LC_ALL, '')
	socket.setdefaulttimeout(30) # 30 seconds
	options, args = parse_cmdline()
	if options.logging_config:
		logging.config.fileConfig(options.logging_config, disable_existing_loggers=False)
	else:
		logging.basicConfig(level=logging.DEBUG)
	if options.redis_host:
		r = redis.StrictRedis(host=options.redis_host, port=options.redis_port, db=0)
		r.sadd('queues', 'feedparser')
		get(None, options.id, options.etag, options.modified, redis=r)
	else:
		for url in args:
			get(url, options.id, options.etag, options.modified)

