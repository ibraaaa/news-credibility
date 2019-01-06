#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os.path
import traceback
import urllib2
import util.const as const
import util.db as db
import util.helper as helper

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class McePagesCrawler(object):
    """ Crawls parts of MCE Watch website. It crawls urls with the format:
        http://mcewatch.com/الأخبار/page/{PAGE_NUM}/?show={trusted | untrusted}
        where PAGE_NUM is the number of the page to be crawled, pages are numbered
        in ascending order according to the date of tagging i.e. first page has latest news.
        
        TODO(ibraaaa): change the naming format, recrawling will overwrite pages.
        Crawled HTML pages are stored to disk with name of the form "PAGE_NUM.html".
        
        Example usage:
        --------------
        crawler = McePagesCrawler(True)  # gets credible news
        crawler.crawl(end=236)           # last page
    """
    def __init__(self, credible):
        self._url = 'http://mcewatch.com/{0}/page/{1}/?show={2}'
        self._pages_dir = const.MCE_PAGES_TRUSTED if credible else const.MCE_PAGES_UNTRUSTED
        self._credible = "trusted" if credible else "untrusted"
        
    def crawl(self, start = 1, end = None):
        assert end
        i = end
        while True:
            if i < start: break
            print urllib2.quote("الأخبار")
            url = self._url.format(urllib2.quote('الأخبار'), i, self._credible)
            print url
            html = urllib2.urlopen(url).read().decode('utf-8')
            helper.WRITE_FILE(os.path.join(self._pages_dir,"{0}.html".format(i)), html.encode('utf-8'))
            i = i - 1
            
class MceComplaintsCrawler(object):
    """ Crawls complaint pages from MCE Watch website. It reads urls of the pages
        to be crawled from the database, downloads the page and stores it to disk.
        
        Example usage:
        --------------
        crawler = MceComplaintsCrawler(False, 1)     # uncredible news crawled from page 1
        crawler.crawl()
    """
    def __init__(self, credible = False, page = None):
        self._credible = credible
        self._complaints_dir = const.MCE_COMPLAINTS_TRUSTED if credible else const.MCE_COMPLAINTS_UNTRUSTED
        self._page = page
        self._db = db.MceWatchIndexOperation()
        
    def crawl(self):
        for mcepage_record in self._db.select(self._page, self._credible):
            print mcepage_record.id, '\t', mcepage_record.url
            html = urllib2.urlopen(mcepage_record.url).read().decode('utf-8')
            helper.WRITE_FILE(os.path.join(self._complaints_dir, "{0}.html".format(mcepage_record.id)), html.encode('utf-8'))

class NewsFromMceCrawler(object):
    @staticmethod
    def __crawl(credible, dir_name, upper_id):
        _db = db.MceWatchIndexOperation()
        for record in _db.get_news_urls_for_no_html(credible):
            try:
                logging.info("{0}\t{1}".format(record.id, record.news_url))
                if record.id < upper_id: continue
                html = urllib2.urlopen(record.news_url).read()
                path = os.path.join(dir_name, "{0}.html".format(record.id))
                helper.WRITE_FILE(path, html)
                _db.update_complaint_html_filepath(path, record.id)
            except Exception:
                print traceback.format_exc()
                
    @staticmethod
    def crawl_trusted(upper_id):
        NewsFromMceCrawler.__crawl(True, const.TRUSTED_NEWS_HTML_BY_MCE, upper_id)
    
    @staticmethod
    def crawl_untrusted(upper_id):
        NewsFromMceCrawler.__crawl(False, const.UNTRUSTED_NEWS_HTML_BY_MCE, upper_id)
    
if __name__ == '__main__':
    #McePagesCrawler(False).crawl(3, 3)
    
    #for i in range(82, 83):
    #    print i
    #    crawler = MceComplaintsCrawler(True, i)
    #    crawler.crawl()
    
    NewsFromMceCrawler.crawl_trusted(7931)
    #NewsFromMceCrawler.crawl_untrusted(7931)