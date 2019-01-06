import lxml.html
import os.path
import parsers.html_parser
import util.const as const
import util.db as db
import util.helper as helper
from parsers.html_parser import HTMLParser

class MceWatchParser(object):    
    @staticmethod
    def parse_pages(html):
        """ Parses MCE Watch pages like this one: http://goo.gl/fkf7R
            It extracts the URLs directing to the detailed complaint
            page of each article. You should expect a list of 9 URLs
            except for the last page which may have a number of URLS in [1-9]. 
        """
        page = lxml.html.fromstring(html)
        return page.xpath("//div[@id='trusted_news']/div[@id='all_news']/div[@class='all_newsholder']/div[@class='all_newsbox clearfix']/a/attribute::href")
    
    @staticmethod
    def parse_complaints(html, credible):
        """ Parses MCE watch Pages like this one: http://goo.gl/1NdvI
            It extracts info about the article being judged and the points
            of judgement. This includes the article URL, the news site,
            the list of complaint text and an expert's reasoning.
        """
        page = lxml.html.fromstring(html)
        complaints = page.xpath("//div[@id='penalites-complains']/p[@class='pentalty-paragraph-complains']/span/child::text()") if not credible else []
        url = page.xpath("//div[@id='comp_holder']/a/attribute::href")[0]
        source = page.xpath("//div[@id='comp_holder']/a/img/attribute::title")
        source = source[0] if len(source) > 0 else ''
        expert_comments = page.xpath("//div[@id='explain']/descendant::strong/descendant::text()") if not credible else ''
        return (complaints, url, const.MCE_WATCH_SOURCES_MAPPING[source] if source else None, '\n'.join(expert_comments))
    
class MceWatchParserRunner(object):
    """ This class has utility methods to run MceWatchParser methods.
    """
    def __init__(self):
        self._db = db.MceWatchIndexOperation()
        self._db.create_tables()
        
    def parse_pages(self, start, end, credible):
        """ Read and parses all html pages in:
             ../data/mce/pages/{trusted | untrusted}/{PAGE}.html
            It populates the a database table 'news_index.MceWatchIndex' with the result of parsing.
        """
        for page in xrange(start, end + 1):
            html = helper.READ_FILE(os.path.join(const.MCE_PAGES_TRUSTED if credible else const.MCE_PAGES_UNTRUSTED, "{0}.html".format(page)))
            urls = MceWatchParser.parse_pages(html)
            self._db.create_entry(urls, page, credible)
            
    def parse_complaints(self, start_id, end_id, credible):
        """ Reads and parses complaint pages from:
             '../data/mce/complaints/{trusted | untrusted}/{PAGE}.html'
            and stores the result in database table 'news_index.MceWatchComplaint'.
        """
        for complaint_id in range(start_id, end_id + 1):
            html = helper.READ_FILE(os.path.join(const.MCE_COMPLAINTS_TRUSTED if credible else const.MCE_COMPLAINTS_UNTRUSTED, "{0}.html".format(complaint_id)))
            (complaints, url, source, expert_comments) = MceWatchParser.parse_complaints(html, credible)
            #print url
            #print source
            #print expert_comments
            #print '***************************************************************************************************************************************************'
            self._db.create_complaint(complaints, url, source, expert_comments, complaint_id)
            
if __name__ == "__main__":
    #MceWatchParserRunner().parse_pages(3, 183, False)
    #MceWatchParserRunner().parse_pages(2, 82, True)
    
    MceWatchParserRunner().parse_complaints(10063, 10267, True)