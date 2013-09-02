import urllib2
import lxml.html as LH

# request a partial download
#url='http://www.python.org/'
url='http://localhost:8000/atom_apostrophe.xml'
req = urllib2.Request(url)
req.headers['Range'] = 'bytes=%s-%s' % (0, 100000)
f = urllib2.urlopen(req)
content=f.read()
# print(content)

# incremental parsing
import feedparser

data = feedparser.parse(content)
str_list = []
for article in data.entries:
	str_list.append(article.get('title', 'null'))

#print len(str_list)
#print str_list
