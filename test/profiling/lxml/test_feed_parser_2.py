
import urllib2
import lxml.html as LH
import feedparser

url='http://localhost:8000/atom_apostrophe.xml'
data = feedparser.parse(url)
y = data.xpath('//title')

#print len(y)

      

