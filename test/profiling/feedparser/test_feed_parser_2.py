import urllib2
import lxml.html as LH

url='http://localhost:8000/atom_apostrophe.xml'

import feedparser

data = feedparser.parse(url)
str_list = []
for article in data.entries:
	str_list.append(article.get('title', 'null'))

#print len(str_list)
#print str_list
