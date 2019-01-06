#!/usr/bin/python
# -*- coding: utf-8 -*-
import nltk
import util.const as const
import util.db as db
import util.helper as helper
import util.sentiwordnet_wrapper as sentiwordnet

class Sentiment(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Sentiment, cls).__new__(cls, *args, **kwargs)
            
        return cls._instance
        
    def init_sentiment_dic(self, english_verbs):
        sentiment_dic = {}
        for verb in english_verbs:
            sentiment_dic[verb] = 0
            for senti_synset in self._swn.senti_synsets(verb, 'v'):
                sentiment_dic[verb] += senti_synset.pos_score - senti_synset.neg_score
        return sentiment_dic
    
    def __init__(self):
        nltk.data.path.append('/home/ibraaaa/nltk_data')
        self._swn = sentiwordnet.SentiWordNet()
        self._db = db.IndexOperation()
        arabic_verbs = helper.READ_LINES(const.ARABIC_VERBS_FILE)
        english_verbs = helper.READ_LINES(const.ENGLISH_VERBS_FILE)
        assert len(arabic_verbs) == len(english_verbs)
        self._arabic_english = {arabic_verbs[i]: english_verbs[i] for i in range(0, len(arabic_verbs))}
        self._sentiment_dic = self.init_sentiment_dic(english_verbs)
        
        verbs_file = '../../../../resources/verbs.csv'
        self._arabic_sentiment_dic = dict(map(lambda k: (k[0].decode('utf-8'), int(k[1]) if k[1] else 0), [(line.split(',')[0], line.split(',')[2].strip()) for line in open(verbs_file)]))
        assert u'يهدد' in self._arabic_sentiment_dic
        
        
    def calc_headline_sentiment_by_english(self, url):
        txt_file_path = '../../../' + helper.HTML_TO_TXT_DIR(self._db.get_path_by_url(url))
        headline = helper.READ_FIRST_LINE(txt_file_path)
        headline = headline.translate(const.TRANSLATE_TABLE)
        score = 0
        for word in headline.split(' '):
            if word in self._arabic_english:
                word = self._arabic_english[word]
                score += self._sentiment_dic[word]
        return score
    
    def calc_headline_sentiment_by_arabic(self, url):
        txt_file_path = '../../../' + helper.HTML_TO_TXT_DIR(self._db.get_path_by_url(url))
        headline = helper.READ_FIRST_LINE(txt_file_path)
        headline = headline.translate(const.TRANSLATE_TABLE)
        score = 0
        for word in headline.split(' '):
            if word in self._arabic_sentiment_dic:
                score += self._arabic_sentiment_dic[word]
        
        return score