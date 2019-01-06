import calendar
import datetime
import dateutil.parser
import os
import pytz
import urllib
import util.const as const
import util.helper as helper

from GoogleReader.const import CONST
from GoogleReader.feed import GoogleFeed
from GoogleReader.reader import GoogleReader

DIR_PATH=const.RSS_URLS_DIR
LABEL_SINCE_FILE=const.LABEL_SINCE_FILE
GOOGLE_ACCOUNT_NAME='master.news.reader@gmail.com'
GOOGLE_ACCOUNT_PASSWORD='Love4Ever'

class GoogleLabelReader(GoogleReader):
    def get_label(self, label_, since_, cont_=None):
        feedurl = CONST.URI_PREFIXE_ATOM + CONST.ATOM_PREFIXE_LABEL + label_

        kwargs = {}
        kwargs['client'] = CONST.AGENT
        kwargs['timestamp'] = self.get_timestamp()
        kwargs['start_time'] = calendar.timegm(
            dateutil.parser.parse(since_).utctimetuple())
        kwargs['order'] = 'o'

        if cont_ != None:
            kwargs['continuation'] = cont_

        urlargs = {}
        self._translate_args(CONST.ATOM_ARGS, urlargs, kwargs)

        atomfeed = self._web.get('{0}?{1}'.format(feedurl,
        urllib.urlencode(urlargs)))
        print('{0}?{1}'.format(feedurl, urllib.urlencode(urlargs)))
        if atomfeed != '':
            return GoogleFeed(atomfeed)

        return None

def extract_links(greader_, label_, since_, cont_ = None, lvl = 1):
    gfeed_ = greader_.get_label(label_, since_, cont_)

    newest_date_ = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
    max_lvl_ = lvl
    url_date_ = {}
    for entry in gfeed_.get_entries():
        newest_date_ = max(dateutil.parser.parse(entry['published']), newest_date_)

        print entry['link']
        url_date_[entry['link']] = entry['published']

    dir_path_ = helper.RSS_LABEL_TO_DIR(label_, False)
    file_name_ = os.path.join(dir_path_, '{0}.json'.format(lvl))
    helper.WRITE_JSON_FILE(file_name_, url_date_)

    if gfeed_.get_continuation() != None:
        ret_date_, ret_lvl_ = extract_links(greader_, label_, since_, gfeed_.get_continuation(), lvl+1)
        newest_date_ = max(newest_date_, ret_date_)
        max_lvl_ = max(max_lvl_, ret_lvl_)

    return newest_date_, max_lvl_


def main():
    greader_ = GoogleLabelReader()
    greader_.identify(GOOGLE_ACCOUNT_NAME, GOOGLE_ACCOUNT_PASSWORD)
    if not greader_.login():
        raise Exception("Can't Login")

    label_since_ = helper.READ_JSON_FILE(LABEL_SINCE_FILE)
    for label_ in sorted(const.RSS_LABELS):
        since_ = str(datetime.datetime(
            1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc))
        start_dir_ = 0
        if label_ in label_since_.keys():
            since_ = label_since_[label_]['date']
            start_dir_ = label_since_[label_]['last_dir']
        last_feed_date_, end_dir_ = extract_links(greader_, label_, since_, None, start_dir_ + 1)
        label_since_[label_]['date'] = str(max(last_feed_date_, dateutil.parser.parse(since_)))
        label_since_[label_]['last_dir'] = end_dir_
        label_since_[label_]['start_dir'] = start_dir_
        print label_, '\t', last_feed_date_, '\t', start_dir_, '\t', end_dir_

    helper.WRITE_JSON_FILE(LABEL_SINCE_FILE, label_since_, True)

if __name__ == '__main__':
    main()
