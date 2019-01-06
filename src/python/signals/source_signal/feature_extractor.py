#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import Counter
import gensim.utils as gutils
import math
import numpy as np
import util.const as const
import util.helper as helper
from sklearn.base import BaseEstimator
from scipy.sparse.coo import coo_matrix
from pydoc import doc

class FeatureExtractor(object):
    def get_features(self, doc):
        raise NotImplementedError
    
    @staticmethod
    def __preprocess(txt):
        raise NotImplementedError
    

class UnigramFeatureExtractor(FeatureExtractor):
    def __init__(self, training_set):
        self._training_set = training_set
        self._idf = UnigramFeatureExtractor.calculate_idf(training_set)
    
    @staticmethod
    def calculate_idf(training_set):
        idf_table = Counter()
        for sample in training_set:
            #tokens = set([helper.NORMALIZE_TOKEN(token) for token in list(gutils.tokenize(sample[0].decode('utf-8')))])
            tokens = set(UnigramFeatureExtractor.__preprocess(sample[0]))
            idf_table.update(Counter(tokens))
                    
        return idf_table
        
    def get_features(self, doc):
        tokens = UnigramFeatureExtractor.__preprocess(doc)
        word_freq = Counter(tokens)
        tfidf = {}
        for word, freq in word_freq.items():
            tfidf[word] = freq * math.log10(len(self._training_set) * 1.0 / (1 + self._idf[word]))
            
        return tfidf
    
    @staticmethod
    def __preprocess(txt):
        txt = txt.decode('utf-8')
        txt = txt.translate(const.TRANSLATE_TABLE)
        tokens = list(gutils.tokenize(txt))
        tokens = [token[2:] if token.startswith(u'ال') else token for token in tokens if len(token) > 2]
        tokens = [token[1:] if token.startswith(u'و') else token for token in tokens]
        tokens = [token.encode('utf-8') for token in tokens]
        return tokens
    
class HasWordFeatureExtractor(FeatureExtractor):
    def __init__(self):
        self._pos_words = set([x.encode('utf-8') for x in [u'قال', u'اوضح', u'اشار', u'انتقد', u'اضاف', u'تابع',
                                                           u'اكد', u'قالت',
                                                           u'اوضحت', u'اكدت', u'اشارت', u'اضافت', u'انتقدت',
                                                           u'تابعت']])
        #مؤتمر
        #لفضائية
        self._social_words = set([x.encode('utf-8') for x in [u'تويتر', u'فيسبوك', u'فيس', u'بوك', u'تغريدة',
                                                              u'تغريدات', u'تغريداته', u'تغريدته', u'برنامجه', u'برنامجها',
                                                              u'تغريدتها', u'تغريداتها',  u'بيان', u'مكالمة', u'لبرنامج']])
        self._neg_words = set([x.encode('utf-8') for x in [u'سيادي', u'مسئول', u'مصادر', u'مصدر']])
        self._neg_grams = set([x.encode('utf-8') for x in [u'مصادر موثوقة', #u'مصدر مسوؤل', u'مصدر مسئول', u'مصدر سيادي مسئول'
                                                           u'مصادر امنية', u'مصادر امنية رفيعة مستوى',#u'مصدر امنى',
                                                           u'مصدر سيادي', u'مصدر قضائي']])
        #وكالة أنباء الأناضول
        self._sources = set([x.encode('utf-8') for x in [u'ا ش ا', u'رويترز', u'فوكس نيوز', u'اسوشيتدبرس']])
        
    @staticmethod
    def _preprocess(txt):
        txt = txt.decode('utf-8')
        txt = txt.translate(const.TRANSLATE_TABLE)
        return txt.encode('utf-8')
    
    @staticmethod
    def _tokenize(txt):
        txt = txt.decode('utf-8')
        tokens = list(gutils.tokenize(txt))
        tokens = [token[2:] if token.startswith(u'ال') else token for token in tokens if len(token) > 2]
        tokens = [token[1:] if token.startswith(u'و') else token for token in tokens]
        tokens = [token.encode('utf-8') for token in tokens]
        return tokens
        
    def get_features(self, doc):
        ####### BEST::######################
        #####ret = [cnt_pos, 3 * cnt_sources, cnt_social]
        #####return (ret / (np.linalg.norm(ret) + 1)).tolist()
        doc = HasWordFeatureExtractor._preprocess(doc)
        cnt_sources = 0
        for source in self._sources:
            if source in doc:
                cnt_sources += 1

        cnt_neg_grams = 0
        for gram in self._neg_grams:
            if gram in doc:
                cnt_neg_grams += 1
                
        tokens = HasWordFeatureExtractor._tokenize(doc)
        cnt_pos = 0
        cnt_neg = 0
        cnt_social = 0
        for token in tokens:
            if token in self._pos_words:
                cnt_pos += 1
            elif token in self._neg_words:
                cnt_neg = 1
            elif token in self._social_words:
                cnt_social += 1
        
        cnt_pos = 0
        for i in xrange(1, len(tokens)):
            if tokens[i - 1] in self._pos_words and tokens[i] not in self._neg_words:
                #print tokens[i - 1], '\t', tokens[i]
                cnt_pos += 1

        #return [1 if cnt_pos > 0 else 0, 1 if cnt_sources > 0 else 0, 1 if cnt_social > 1 else 0]
        
        return [cnt_pos, 3*cnt_sources, cnt_social]
        #ret = [cnt_pos, 5 * cnt_sources, 3 * cnt_social, cnt_neg_grams]
        #return (ret / (np.linalg.norm(ret) + 1)).tolist()
        #return [cnt_neg_grams]
                
    def get_feature_names(self):
        return [u'has_pos_word', u'has_source', u'has_social', u'has_neg_ngram']
        
class SourceFeatureExtractor(FeatureExtractor):
    def __init__(self):
        self._social_words = set([x for x in [u'تويتر', u'فيسبوك', u'فيس', u'بوك', u'تغريدة',
                                              u'تغريدات', u'تغريداته', u'تغريدته', u'برنامجه', u'برنامجها',
                                              u'تغريدتها', u'تغريداتها',  u'بيان', u'مكالمة', u'لبرنامج',
                                              u'برنامج', u'تصريحات', u'لقاء', u'اجتماع', u'هاتفي',
                                              u'تليفوني', u'مؤتمر', u'لقائه', u'جلسه', u'ندوه']])
        self._pos_words = set([x for x in [u'قال', u'اوضح', u'اشار', u'انتقد', u'اضاف', u'تابع',
                                           u'اكد', u'قالت', u'اوضحت', u'اكدت', u'اشارت', u'اضافت', u'انتقدت',
                                           u'تابعت', u'نفي', u'ناقشت']])
        
        self._neg_words = set([x.encode('utf-8') for x in [u'سيادي', u'مسئول', u'مصادر', u'مصدر']])
        self._sources = set([x.encode('utf-8') for x in [u'ا ش ا', u'رويترز', u'فوكس نيوز', u'اسوشيتدبرس', u'اش ا']])
        
    def get_features(self, doc):
        norm_doc = SourceFeatureExtractor._preprocess(doc)
        tokens = SourceFeatureExtractor._tokenize(norm_doc)
        cnt_social = 0
        cnt_pos = 0
        pos_i = 0
        social_i = 0
        for i in xrange(0, len(tokens)):
            for w in self._social_words:
                done = False
                if w in tokens[i]:
                    #print tokens[i]
                    cnt_social += 1
                    social_i = i + 1
                    done = True
                    break
            if done: break
            
        tokens = SourceFeatureExtractor._postprocess(tokens)
        for i in xrange(0, len(tokens)):
            #print tokens[i]
            if tokens[i] in self._pos_words:
                #print tokens[i]
                cnt_pos += 1
                pos_i = i + 1
                #break
                
        dist = 1
        if cnt_pos * cnt_social > 0:
            dist = abs(pos_i - social_i)*1.0 / len(tokens)
            
        cnt_sources = 0
        for source in self._sources:
            if source in norm_doc:
                cnt_sources += 1
        cnt_x = 0
        for i in xrange(0, len(tokens) - 1):
            if u'خلال' == tokens[i] and tokens[i + 1] in self._social_words:
                cnt_x = 1
                #print tokens[i], '\t', tokens[i + 1]
                break
        #return [cnt_x, min(1, cnt_social), cnt_pos, min(1, cnt_sources)]
        return [3 * min(1, cnt_sources)* 1.0, min(1, cnt_pos) * 1.0]
        #ret = [min(1, cnt_sources) * 3.0, cnt_social, min(1, cnt_pos)]
        #return ret / (np.linalg.norm(ret) + 1)
        #return [min(1, cnt_pos)*1.0, min(1, cnt_sources)*3.0, min(1, cnt_social) * 1.0]
        
    def get_feature_names(self):
        return ['source', 'social', 'pos']
        #return [u'has_khelal', u'has_social', u'has_pos', u'has_sources']
    
    @staticmethod
    def _preprocess(txt):
        txt = txt.decode('utf-8')
        txt = txt.translate(const.TRANSLATE_TABLE)
        return txt.encode('utf-8')
    
    @staticmethod
    def _tokenize(txt):
        txt = txt.decode('utf-8')
        tokens = list(gutils.tokenize(txt))
        #tokens = [token.encode('utf-8') for token in tokens]
        #tokens = [unicode(token) for token in tokens]
        return tokens
    
    @staticmethod
    def _postprocess(tokens):
        tokens = [token[2:] if token.startswith(u'ال') else token for token in tokens if len(token) > 2]
        tokens = [token[1:] if token.startswith(u'و') else token for token in tokens]
        return tokens
         
class WhenFeatureExtractor(FeatureExtractor):
    def __init__(self):
        self._friday = u'الجمعة'.encode('utf-8')
        self._today = u'اليوم'.encode('utf-8')
        self._seven = u'السابع'.encode('utf-8')
        self._news = u'اخبار'.encode('utf-8')
        self._prayers = u'صلاة'.encode('utf-8')
        self._egyptian = u'المصري'.encode('utf-8')
        self._elhayah = u'الحياة'.encode('utf-8')
        
        self._pos_words = [x.encode('utf-8') for x in [ u'امس', u'مساء', u'صباح', u'غد', u'يوم' ]]
        self._week_days = [x.encode('utf-8') for x in [ u'الجمعة', u'السبت', u'الاحد', u'الاثنين',
                                                        u'الثلاثاء', u'الاربعاء', u'الخميس' ]]
        self._other_days = [x.encode('utf-8') for x in [u'اليوم', u'امس']]
        self._neg_suffix = [x.encode('utf-8') for x in [u'الماضي', u'المقبل', u'السابع']]
        self._sources = set([x.encode('utf-8') for x in [u'ا ش ا', u'رويترز', u'فوكس نيوز', u'اسوشيتدبرس', u'انباء الشرق الاوسط']])
        
        self._social_words = set([x.encode('utf-8') for x in [u'تويتر', u'فيسبوك', u'فيس', u'بوك', u'تغريدة',
                                                              u'تغريدات', u'تغريداته', u'تغريدته', u'برنامجه', u'برنامجها',
                                                              u'تغريدتها', u'تغريداتها',  u'بيان', u'مكالمة',
                                                              u'لبرنامج', u'لفضائية', u'مؤتمر', u'تصريح', u'تصريحات']])
    
    @staticmethod
    def _preprocess(txt):
        txt = txt.decode('utf-8')
        txt = txt.translate(const.TRANSLATE_TABLE)
        return txt.encode('utf-8')
    
    @staticmethod
    def _tokenize(txt):
        txt = txt.decode('utf-8')
        tokens = list(gutils.tokenize(txt))
        tokens = [token.encode('utf-8') for token in tokens]
        return tokens
    
    @staticmethod
    def _postprocess(tokens):
        tokens = [token[2:] if token.startswith(u'ال'.encode('utf-8')) else token for token in tokens if len(token) > 2]
        tokens = [token[1:] if token.startswith(u'و'.encode('utf-8')) else token for token in tokens]
        return tokens
    
    def get_features(self, doc):
        norm_doc = WhenFeatureExtractor._preprocess(doc)
        monz_kaleel = 1 if u'منذ قليل'.encode('utf-8') in norm_doc or u'قبل قليل'.encode('utf-8') in norm_doc else 0
        cnt_week_days = 0
        week_dist = 1        
        tokens = WhenFeatureExtractor._tokenize(norm_doc)
        word_index = -1
        for i in xrange(0, len(tokens)):
            if tokens[i] in self._week_days + self._other_days:
                cnt_week_days += 1
                week_dist = (i + 1.0) / len(tokens)
                word_index = i
                cnt_week_days = 1
                # ignore salat el gom3a
                if i > 0 and tokens[i] == self._friday and tokens[i - 1] == self._prayers:
                    #continue
                    break
                
                # ignore akhbar alyom
                if i > 0 and tokens[i] == self._today and tokens[i - 1] == self._news:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue

                # ignore alyom alsabe3
                if i < len(tokens) - 1 and tokens[i] == self._today and tokens[i + 1] == self._seven:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue
                
                # ignore almasry alyom
                if i > 0 and tokens[i] == self._today and tokens[i - 1] == self._egyptian:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue
                break
        
        if monz_kaleel:
            week_dist = 0
            cnt_week_days = 1
        #neg_suffix = 0
        #if word_index > -1 and word_index < len(tokens) - 1 and tokens[word_index] in self._week_days:
            #if tokens[word_index + 1] in self._neg_suffix:
                #neg_suffix = 0.5
                
        #if word_index > 0 and tokens[word_index] in self._week_days and tokens[word_index - 1] in [u'اليوم'.encode('utf-8')]:
        #    week_dist = 0
         
        for i in xrange(0, len(tokens) - 1):
            if tokens[i] in self._other_days and tokens[i + 1] in self._week_days:
                week_dist = 0
                #cnt_week_days = 1
            
        cnt_sources = 0
        for source in self._sources:
            if source in norm_doc:
                cnt_sources += 1
        
        cnt_social = 1
        bin_social = 1
        if word_index != -1:
            for i in xrange(max(0, word_index - 10), min(word_index + 10, len(tokens))):
                if tokens[i] in self._social_words:
                    cnt_social = min(abs(i - word_index) * 1.0 / 10, cnt_social)
                    bin_social = 0
        
        cnt_pos = 0
        dist = 0
        for i in xrange(0, len(tokens)):
            if tokens[i] in self._pos_words:
                cnt_pos += 1
                if dist == 0: dist = i + 1
         
        #ret = [cnt_week_days, week_dist]
        #return (ret / (np.linalg.norm(ret) + 1)).tolist()       
        #return [math.exp(1-week_dist), cnt_social, neg_suffix] 
        #return [min(1, cnt_sources)]
        #return [cnt_week_days, monz_kaleel, cnt_social]
        
        #ret = [math.exp(1 - week_dist), monz_kaleel, cnt_social]
        #return ret / (np.linalg.norm(ret))
        #return [cnt_week_days * 1.0]
        return [math.exp(1 - week_dist), cnt_social]
    
    def try_features(self, doc):
        norm_doc = WhenFeatureExtractor._preprocess(doc)
        monz_kaleel = 1 if u'منذ قليل'.encode('utf-8') in norm_doc or u'قبل قليل'.encode('utf-8') in norm_doc else 0    
        cnt_week_days = 0
        week_dist = 1        
        tokens = WhenFeatureExtractor._tokenize(norm_doc)
        word_index = -1
        for i in xrange(0, len(tokens)):
            #if tokens[i] == u'منذ'.encode('utf-8') or tokens[i] == u'قبل'.encode('utf-8'):
            #    if i < len(tokens) - 1 and tokens[i + 1] == u'قليل'.encode('utf-8'):
            #        cnt_week_days = 1
            #        week_dist = (i + 1.0) / len(tokens)
            #        word_index = i
            #        break
            if tokens[i] in self._week_days + self._other_days:
                week_dist = (i + 1.0) / len(tokens)
                word_index = i
                cnt_week_days = 1
                
                #if tokens[i] == u'منذ'.encode('utf-8') or tokens[i] == u'قبل'.encode('utf-8'):
                #    week_dist = 0
                #    if i == len(tokens) - 1 or tokens[i + 1] != u'قليل'.encode('utf-8'):
                #        week_dist = 1
                #        word_index = -1
                #        cnt_week_days = 0
                #        continue
                
                # ignore salat el gom3a
                #if i > 0 and tokens[i] == self._friday and tokens[i - 1] == self._prayers:
                #    break
                
                # ignore akhbar alyom
                if i > 0 and tokens[i] == self._today and tokens[i - 1] == self._news:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue

                # ignore alyom alsabe3
                if i < len(tokens) - 1 and tokens[i] == self._today and tokens[i + 1] == self._seven:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue
                
                # ignore almasry alyom
                if i > 0 and tokens[i] == self._today and tokens[i - 1] == self._egyptian:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue

                # Consider adding 'الحياة اليوم'.
                if i > 0 and tokens[i] == self._today and tokens[i - 1] == self._elhayah:
                    week_dist = 1
                    word_index = -1
                    cnt_week_days = 0
                    continue
                break
        
         
        for i in xrange(0, len(tokens) - 1):
            if tokens[i] in self._other_days and tokens[i + 1] in self._week_days:
                week_dist = 0
                cnt_week_days = 1
        
        cnt_social = 1
        bin_social = 1
        if word_index != -1:
            for i in xrange(max(0, word_index - 10), min(word_index + 10, len(tokens))):
                if tokens[i] in self._social_words:
                    cnt_social = min(abs(i - word_index) * 1.0 / 10, cnt_social)
                    if i < word_index: cnt_social *= -1
                    bin_social = 0
                    
        if monz_kaleel:
            week_dist = 0
            cnt_week_days = 1
         
        return [math.exp(1 - week_dist), cnt_social]
     
    def get_feature_names(self):
        return [u'distance', u'social']

class ScikitWordFeature(BaseEstimator):
    def __init__(self, source_signal = True):
        if source_signal:
            self._feature_extractor = SourceFeatureExtractor()#HasWordFeatureExtractor()
        else:
            self._feature_extractor = WhenFeatureExtractor()
        
    def fit(self, raw_documents, y = None):
        return self
    
    def fit_transform(self, raw_documents, y = None):
        features = []
        for doc in raw_documents:
            features.append(self._feature_extractor.get_features(doc))
            #features.append(self._feature_extractor.try_features(doc))
            
        return coo_matrix(features)
    
    def transform(self, raw_documents):
        return self.fit_transform(raw_documents, None)
    
    def get_feature_names(self):
        return self._feature_extractor.get_feature_names()
    
class WhenFeatureDev(ScikitWordFeature):
    def __init__(self, days = []):
        super(WhenFeatureDev, self).__init__(source_signal = False)
        self._feature_extractor._week_days = days
        self._feature_extractor._other_days = []
        
    def fit_transform(self, raw_documents, y = None):
        features = []
        for doc in raw_documents:
            features.append(self._feature_extractor.try_features(doc))
            
        return coo_matrix(features)