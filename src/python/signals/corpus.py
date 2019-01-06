#!/usr/bin/python
# -*- coding: utf-8 -*-

import dateutil.parser
import gensim.utils as gutils
import os.path
import util.const as const
import util.db as db
import util.helper as helper

from nltk.stem import ISRIStemmer

class NewsCorpus(object):
    """ An implementation of a corpus that provides an iterator method.
        It uses RSS labels to construct index path and then load indexes one by one in memory.
        For each index, parsed documents are yielded one by one.

        TODO: a simple tokenize method is used to tokenize the text, a more sophisticated preprocessing function is needed!
    """
    def __init__(self, rss_labels_, start_date_ = None):
        self._indexes = [(os.path.join(const.RSS_HTML_INDEX_DIR, "{0}.json".format(label)), label) for label in rss_labels_]
        if start_date_:
            self._start_date = dateutil.parser.parse(start_date_)
        else:
            self._start_date = None

    def __iter__(self):
        for index_file, label in self._indexes:
            index_ = helper.READ_JSON_FILE(index_file)
            for html_file, value in index_.items():
                if 'parsed' not in value or value['parsed'] == False: continue
                if self._start_date and self._start_date > dateutil.parser.parse(value['date']): continue
                txt_file = helper.HTML_TO_TXT_DIR(html_file)
                yield {
                        'id': txt_file,
                        'tokens': list(gutils.tokenize(helper.READ_FILE(txt_file))),
                        'payload': {
                                    'url': value['url'],
                                    'date': value['date'],
                                    'news_site': label.split('-')[0],
                                    'rss_label': label
                                   }
                      }


class DBNewsCorpus(object):
    def __init__(self, rss_labels_, start_date_ = None, end_date_ = None, stem_ = False):
        self._db = db.IndexOperation()
        self._rss_labels = rss_labels_
        
        self._start_date = None
        if start_date_: self._start_date = dateutil.parser.parse(start_date_)
        self._end_date = None
        if end_date_: self._end_date = dateutil.parser.parse(end_date_)
            
        self._translate_table = const.TRANSLATE_TABLE
        self._stemmer = None
        if stem_: self._stemmer = ISRIStemmer()

    def __get_tokens(self, txt):
        txt = txt.decode('utf-8')
        assert type(txt) == unicode
        txt = txt.translate(self._translate_table)
        tokens = list(gutils.tokenize(txt))
        tokens = [token[2:].encode('utf-8') if token.startswith(u'ال') else token.encode('utf-8') for token in tokens if len(token) > 3]
        if self._stemmer: tokens = [self._stemmer.stem(token) for token in tokens]
        return tokens
        
    def __iter__(self):
        for label in self._rss_labels:
            for index in self._db.select_by_rss_label(label):
                if self._start_date and self._start_date > index.date: continue
                if self._end_date and self._end_date < index.date: continue
                txt_file = helper.HTML_TO_TXT_DIR(index.file_path)
                #self._db.set_in_train(index.file_path)
                yield {
                        'id': txt_file,
                        'tokens': self.__get_tokens(helper.READ_FILE(txt_file)),
                        'payload': {
                                    'url': index.url,
                                    'date': index.date,
                                    'news_site': index.news_site,
                                    'rss_label': index.rss_label
                                   }
                      }