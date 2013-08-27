import sys

if sys.hexversion < 0x0240000:
	print >> sys.stderr, 'The python version is too old (%s)' % \
		(sys.version.split()[0])
	print >> sys.stderr, 'At least Python 2.4 is required'
	sys.exit(1)

import unittest
 
# ---------------------------------------------------------

import feedparser
import simplejson as json

from feeder.parser import process_data, process_url

class TestParsedFeed(unittest.TestCase):
    ''' Class for basic tests on feeds (ideally abstract) '''

    def private_check_json_output(self, ret_str):
        ''' Helper method to check critical fields in a JSON-encoded output string '''
        ret_json = json.loads(ret_str)
        self.assertTrue(len(ret_json['title']) > 10)
        # self.assertTrue(len(ret_json['updated']) > 10)
        #self.assertEqual(ret_json['updated'], 'me')
        for article in ret_json['articles']:
           self.assertTrue(len(article['title']) > 1)
           self.assertTrue(len(article['published']) > 10)
        return ret_json 

    def private_test_url_process(self, url):
        ''' Helper method to test the process_data method: parses a url, 
               and then delegates checking the output String '''
        data = feedparser.parse(url)
        ret_str = process_data(data, None)
        return self.private_check_json_output(ret_str)
     
# ---------------------------------------------------------

import re 

class TestFeederDates(TestParsedFeed): 

    targetPattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")  

    def test_rss_process(self):
        ret_json = self.private_test_url_process('test/data/rss.xml')
        self.assertEqual(ret_json['articles'][0]['published'], '2013-08-19 17:56:08')
        for article in ret_json['articles']:
           matched = self.targetPattern.match ( article['published'] )
           self.assertNotEqual(matched , None)
        
    def test_atom_process(self):
        ret_json = self.private_test_url_process('test/data/atom_flat.xml')
        self.assertEqual(ret_json['articles'][0]['published'], '2013-08-19 16:03:53')
        for article in ret_json['articles']:
           matched = self.targetPattern.match ( article['published'] )
           self.assertNotEqual(matched , None)

    def test_distant_process(self):
        ''' Strangely, this test on a local file fails '''
        ret_str = process_url('http://linuxfr.org', None, None)
        ret_json = self.private_check_json_output(ret_str)
        matched = self.targetPattern.match ( ret_json['updated'] )
        self.assertNotEqual(matched , None)
        
# ---------------------------------------------------------

class TestFeederBasics(TestParsedFeed):

    def test_rss_process(self):
        self.private_test_url_process('test/data/rss.xml')
        
    def test_rss_dates(self):
        self.private_test_url_process('test/data/rss.xml')
         
    def test_atom_process(self):
        self.private_test_url_process('test/data/atom_flat.xml')

    def test_atom_apostrophe_process(self):
        self.private_test_url_process('test/data/atom_apostrophe.xml')

    def test_html_homepage(self):
        ret_str = process_url('http://www.lemonde.fr', None, None)
        self.private_check_json_output(ret_str)

# ---------------------------------------------------------

from feeder.HttpHelpers import is_html, get_feed_url

class TestHttpHelpers(unittest.TestCase):

    def test_is_html(self):
        targets = {
            'http://www.bing.com': True,
            'http://linuxfr.org/news.atom': False,
            'http://www.lemonde.fr/rss/une.xml': False
        }
        for url, isHtml in targets.items():
           self.assertEquals(is_html(url) , isHtml)

    def test_get_feed_url(self):
        targets = {
            'http://www.bing.com': None,
            'http://linuxfr.org': 'http://linuxfr.org/news.atom',
            'http://www.lemonde.fr': 'http://www.lemonde.fr/rss/une.xml',
            'http://www.python.org': 'http://www.python.org/channews.rdf',
        }
        for base_url, feed_url in targets.items():
           self.assertEquals(get_feed_url(base_url) , feed_url)
    
# ---------------------------------------------------------
      
if __name__ == '__main__':
    unittest.main()
    
