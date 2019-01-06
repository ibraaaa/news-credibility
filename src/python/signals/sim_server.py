import logging
#import math
import signals.corpus as NewsCorpus
import util.const as const
import util.db as db
import util.helper as helper
import traceback;

from datetime import datetime
from datetime import timedelta
from simserver import SessionServer

class SimServer(object):
    def __init__(self, server_path = '/home/ibraaaa/servers/my_server/', start_date = None, end_date = None, stem_ = False):
        try:
            logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
            self._corpus = NewsCorpus.DBNewsCorpus(const.RSS_POLITICS_LABELS, start_date, end_date, stem_)
            self._service = SessionServer(server_path)
            self._db = db.IndexOperation()
        except:
            print traceback.format_exc()

    def train(self, method = 'lsi'):
        self._service.train(self._corpus, method = method)

    def index(self, corpus=None):
        if not corpus:
            corpus = self._corpus
        self._service.index(corpus)
        
    def drop_index(self):
        self._service.drop_index()
        
    def query(self, query_, max_results_ = 10000):
        """ Queries the index for the passed query by either text, path of file on disk (DOC ID)
            or URL.
            
            Exceptions:
                DBException: if query is a URL that is not found in DB
                ValueError: if query is ID or URL whose corresponding ID is not indexed.
                All other exceptions are allowed to propagate to the caller.
        """
        # TODO: if a query asks for a document that is not indexed, then:
        # either read it and use the text to query OR index uptill its date!
        if query_[:4] == 'http':
            query_ = helper.HTML_TO_TXT_DIR(self._db.get_path_by_url(query_))
        return self._service.find_similar(query_, max_results = max_results_), self._db.get_date_by_path(query_.replace('txt', 'html'))

    def rank(self, result, query_date):
        mod = sorted(result, reverse = False, key = lambda k: abs(k[2]['date'] - query_date))
        mod = sorted(mod[:min(100, len(mod))], reverse = True, key = lambda k: k[1])
        return mod[:min(20, len(mod))]
        #for r in result:
        #    now_timestamp = calendar.timegm(datetime.utcnow().utctimetuple())
        #    timestamp = calendar.timegm(dateutil.parser.parse(r[2]['date']).utctimetuple())
        #    r += (1 / math.exp(math.log(abs(timestamp - now_timestamp))) * math.exp(r[1]),)
        #    mod.append(r)
        
        #return sorted(mod[:min(20, len(mod))], reverse = True, key = lambda k: k[1])

if __name__ == '__main__':
    start_date_ = datetime(2013, 02, 28)#datetime(2013, 02, 14, 0, 0, 0)
    end_date_ = start_date_ + timedelta(days = 30)#days = 15
    server = SimServer('/home/ibraaaa/servers/1mon_preprocess/', str(start_date_), str(end_date_), stem_=False)
    #server.train(method = 'lsi')
    index_corpus = NewsCorpus.DBNewsCorpus(const.RSS_LABELS, str(end_date_ - timedelta(days=60)))
    server.index(index_corpus)