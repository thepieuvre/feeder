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
parser=LH.HTMLParser()
parser.feed(content)
x = parser.close()
y = x.xpath('//title')

print len(y)
