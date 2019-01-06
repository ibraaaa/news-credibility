"""
To use this module to crawl news articles from URLs that have been
downloaded from RSS, do: HTMLCrawlerRunner().crawl_rss_html([list of RSS labels])

To use this module to crawl news articles from URLs that have been
downloaded from Facebook, do: HTMLCrawlerRunner().crawl_fb_html([list of fb pages])
"""

import calendar
import datetime
import dateutil.parser
import os
import time
import traceback
import urllib2
import uuid
import util.const as CONST
import util.db as db
import util.helper as helper


from multiprocessing import Pool

class HTMLCrawler(object):
    """ Base HTML crawler, it holds common logic. Don't instantiate it directly.
        Use one of the derived classes 'FacebookHTMLCrawler' or 'RSSHTMLCrawler'.
    """
    def __init__(self, url_dir_, html_dir_, log_dir_, index_dir_, page_):
        """ Parameterized constructor that  gets called by constructors of
            derived classes. Initializes local members.
        """
        self._url_dir = url_dir_
        self._html_dir = html_dir_
        self._logger = helper.Logger(log_dir_)
        self._index_dir = index_dir_
        self._page = page_
        self._db = db.IndexOperation()

        print self._url_dir, "\t", self._html_dir, "\t", self._index_dir


    def crawl(self, i):
        """ Does the actual logic of reading urls from json files, then
            performing HTTP request to download the html files, write
            the downloaded files to disk and updates index files.

            @param file_name_: json file to read the URLs from
        """
        file_name_ = '{0}.json'.format(i)
        self._logger.log_info('{0}\t{1}'.format(self._page, file_name_))
        urls_ = self.urls_from_json(os.path.join(self._url_dir, file_name_))
        for url, created_time in urls_.items():
            #if url[:11] != 'http://www.' and url[:12] != 'https://www.':
            #    if url[:5] == 'http:': url = 'http://www.' + url[7:]
            #    if url[:6] == 'https:': url = 'https://www.' + url[8:]

            url = url.encode('utf-8')
            tries = 0
            while tries < 10:
                time.sleep(tries * 6)
                try:
                    req_ = urllib2.urlopen(url)
                    html_ = req_.read()
                    # Expected 'utf-8' in all except 'elfagr'
                    encoding_ = req_.headers['content-type'].split('charset=')[-1]
                    if 'charset=' in req_.headers['content-type'] and encoding_ != 'utf-8':
                        html_ = html_.decode(encoding_).encode('utf-8')
                    self.write_html(html_, url, created_time,
                        os.path.join(self._html_dir, str(i)))
                    break
                except urllib2.HTTPError:
                    self._logger.log_error(url, traceback.format_exc())
                    tries = tries + 5
                except Exception:
                    self._logger.log_error(url, traceback.format_exc())
                    tries = tries + 1


    def write_html(self, html_, url_, created_time_, html_dir_):
        """ Writes HTML data to file and updates index files.

            @param html_: HTML data to write
            @param url_: URL used to download the HTML data
            @param created_time_: time HTML article was published
            @param html_dir_: relative path to directory to store HTML file.
        """
        date_time_ = datetime.datetime.fromtimestamp(created_time_)
        if not os.path.exists(html_dir_): os.mkdir(html_dir_)
        file_path_ = os.path.join(html_dir_,
            '{0}#{1}.html'.format(date_time_, uuid.uuid4()))
        helper.WRITE_FILE(file_path_, html_)
        self._logger.log_info(file_path_)

        self._db.create_entry(file_path_, url_, date_time_, self._page)
        # ****************** Stopped updating json files in branch: no_json_index, 26-03-2013***************
        #helper.UPDATE_JSON_FILE(
        #    os.path.join(self._index_dir,
        #        '{0}.json'.format(self._page)),
        #    file_path_,
        #    {'url': url_, 'date': str(date_time_)},
        #    True)


    def urls_from_json(self, json_file_):
        pass


# 'almasryalyoum' ignored for now. Alahram has 1.json and 2.json missing,'bbcarabicnews'
# needs FB crawling
class FacebookHTMLCrawler(HTMLCrawler):
    """ This class crawls news articles whose links were downloaded from
    Facebook pages. It extends HTMLCrawler.
    """
    def __init__(self, url_dir_, html_dir_, log_dir_, index_dir_, page_):
        """ Parameterized constructor.
            All directories (except the logs) will have the format
            '../data/fb/{urls|html}/{page_}/'

            @param url_dir_: relative path to dir holding json files of URLs to news articles.
            @param html_dir_: relative path to dir that will hold crawled HTML files
            @param log_dir_: relative path to dir where logs will be saved
            @param index_dir_: relative path to dir where index files are stored
            @param page_: the facebook page name corresponding to the news site,
                          it is also used as the dir name.
        """
        super(FacebookHTMLCrawler, self).__init__(url_dir_, html_dir_,
        log_dir_, index_dir_, page_)

    def crawl(self):
        """ Reads the json files and for each one delegates the logic to the
        base class version.
        """
        json_files_ = [files for root, directory, files in os.walk(self._url_dir)][0]
        print len(json_files_)
        for i in range(20, 31):#FB 20, 31
            file_name_ = '{0}.json'.format(i)
            if file_name_ not in json_files_:
                break;
            super(FacebookHTMLCrawler, self).crawl(i)


    def urls_from_json(self, json_file_):
        """ Reads and parses a json file holding URLs for news articles
            downloaded from Facebook.

            @param json_file_: the relative path to the json file. It should be
                               something like: '../data/fb/urls/{page_}/xxx.json'
        """

        try:
            json_data_ = helper.READ_JSON_FILE(json_file_)
            urls_ = {}
            for entry_ in json_data_:
                urls_[entry_['attachment']['href']] = entry_['created_time']

            return urls_
        except Exception:
            self._logger.log_error("Error parsing JSON", traceback.format_exc())
            temp_ = {}
            return temp_


class RSSHTMLCrawler(HTMLCrawler):
    def __init__(self, url_dir_, html_dir_, log_dir_, index_dir_, label_, start_dir_):
        """ Parameterized constructor.
            All directories (except the logs) will have the format
            '../data/rss/{urls|html}/{page_}/'

            @param url_dir_: relative path to dir holding json files of URLs to news articles.
            @param html_dir_: relative path to dir that will hold crawled HTML files
            @param log_dir_: relative path to dir where logs will be saved
            @param index_dir_: relative path to dir where index files are stored
            @param label_: the google reader label corresponding to the news site,
                           it is also used as the dir name.
            @param start_dir_: the json file number to start processing
        """
        super(RSSHTMLCrawler, self).__init__(url_dir_, html_dir_, log_dir_,
        index_dir_, label_)
        self._start_dir = start_dir_

    def crawl(self):
        """ Reads the URLs json files and for each one delegates the logic to the
        base class version.
        """
        json_files_ = [files for root, directory, files in os.walk(self._url_dir)][0]
        print len(json_files_)
        for i in range(self._start_dir, self._start_dir + 400):#FB 20, 31
            file_name_ = '{0}.json'.format(i)
            if file_name_ not in json_files_:
                break;
            super(RSSHTMLCrawler, self).crawl(i)

    def urls_from_json(self, json_file_):
        """ Reads and parses a json file holding URLs for news articles
            downloaded from Google reader.

            @param json_file_: the relative path to the json file. It should be
                               something like: '../data/rss/urls/{label_}/xxx.json'
        """
        try:
            json_data_ = helper.READ_JSON_FILE(json_file_)
            urls_ = {}
            for url, date in json_data_.items():
                utc_tuple_ = dateutil.parser.parse(date).utctimetuple()
                urls_[url] = calendar.timegm(utc_tuple_)

            return urls_
        except Exception:
            self._logger.log_error("Error parsing JSON", traceback.format_exc())
            temp_ = {}
            return temp_


class HTMLCrawlerRunner:
    """ Create instance of this class to run a crawler. It has two methods:
        -|crawl_fb_html| runs the crawler to get data from URLs that were
         downloaded from Facebook, and

        -|crawl_rss_html| runs the crawler to get data from URLS that were
         downloaded from Google reader.

         Both methods run multiple processes each handles crawling from a
         different news site.
    """
    def crawl_fb_html(self, pages_, num_processes_=8):
        """ Crawls HTML articles from URLs that were downloaded from facebook.
            Runs a number of processes each handles crawling data from a
            different news site.

            @param pages_: list of news sites facebook pages
            @param num_processes_: number of processes to run, defaults to 8.
        """
        urls_dirs_ = [helper.FB_PAGE_TO_DIR(page, False) for page in pages_]
        html_dirs_ = [helper.FB_PAGE_TO_DIR(page, True) for page in pages_]

        crawlers_ = []
        for i in range(0, len(urls_dirs_)):
            crawlers_.append(FacebookHTMLCrawler(urls_dirs_[i],
                html_dirs_[i], CONST.FB_LOG_DIR,
                CONST.FB_HTML_INDEX_DIR, pages_[i]))

        pool = Pool(processes=num_processes_)
        pool.map(RUN_CRAWLER, crawlers_)
        pool.close()
        pool.join()
        print "DONE"


    def crawl_rss_html(self, labels_):
        """ Crawls HTML articles from URLs that were downloaded from Google Reader.
            Runs a number of processes, each handles crawling data from a
            different news site.

            @param labels_: list of news sites RSS labels
            @param num_processes_: number of processes to run, defaults to 8.
        """

        urls_dirs_ = [helper.RSS_LABEL_TO_DIR(label, False) for label in labels_]
        html_dirs_ = [helper.RSS_LABEL_TO_DIR(label, True) for label in labels_]
        label_since_ = helper.READ_JSON_FILE(CONST.LABEL_SINCE_FILE)

        crawlers_ = []
        for i in range(0, len(urls_dirs_)):
            crawlers_.append(RSSHTMLCrawler(urls_dirs_[i],
                html_dirs_[i], CONST.RSS_LOG_DIR,
                CONST.RSS_HTML_INDEX_DIR, labels_[i],
                label_since_[labels_[i]]['start_dir'] + 1))

        pool = Pool(processes=16)
        pool.map(RUN_CRAWLER, crawlers_)
        pool.close()
        pool.join()
        print "DONE"


def RUN_CRAWLER(crawler_):
    """ Takes an instance of FacebookHTMLCrawler or RSSHTMLCrawler
        and runs the crawler.
    """
    crawler_.crawl()

if __name__ == '__main__':
    HTMLCrawlerRunner().crawl_rss_html(CONST.RSS_LABELS)
    