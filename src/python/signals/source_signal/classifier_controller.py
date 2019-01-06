#!/usr/bin/python
# -*- coding: utf-8 -*-


from itertools import cycle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from nltk.stem.isri import ISRIStemmer
from signals.source_signal.feature_extractor import UnigramFeatureExtractor,\
    HasWordFeatureExtractor, ScikitWordFeature, SourceFeatureExtractor,\
    WhenFeatureDev
from signals.source_signal.data_set import NoSourceAndNoHowInfoGotDataSet,\
    NoSourceInfoDataset, NoWhenDataset
from sklearn import cross_validation
from sklearn import metrics
from sklearn import preprocessing
from sklearn.decomposition.pca import RandomizedPCA
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer,\
    TfidfVectorizer
from sklearn.feature_selection.univariate_selection import SelectKBest, chi2
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model.stochastic_gradient import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.decomposition import PCA
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from util import const
from util import helper

import gensim.utils as gutils
import nltk
import numpy as np
import os.path
import pylab as pl
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from nltk.corpus.reader.rte import norm

class ClassifierController(object):
    def __init__(self, classifier_type = 'NB'):
        self._classifier_type = classifier_type
        self._data_set = NoSourceAndNoHowInfoGotDataSet()
        self._training_set = self._data_set.get_training_set()
        self._feature_extractor = UnigramFeatureExtractor(self._training_set)
        
    def train(self):
        training_set = []
        for training_sample, label in self._training_set:
            training_set.append((self._feature_extractor.get_features(training_sample), label))
            
        if self._classifier_type == 'NB':
            self._classifier = nltk.NaiveBayesClassifier.train(training_set)
        assert self._classifier is not None
        
        print 'Accuracy on Training Set: %.2f' % (nltk.classify.accuracy(self._classifier, training_set) * 100.0)
        
    def classify(self, txt):
        feature_set = self._feature_extractor.get_features(txt)
        return self._classifier.classify(feature_set)
    
    def classify_validation_set(self):
        assert self._classifier is not None
        validation_set = []
        for test_sample, label in self._data_set.get_validation_set():
            validation_set.append((self._feature_extractor.get_features(test_sample), label))
        
        print 'Size of Validation Set: ', len(validation_set)
        print 'Accuracy on Validation Set: %.2f' % (nltk.classify.accuracy(self._classifier, validation_set) * 100.0)
        
    def classify_test_set(self):
        assert self._classifier is not None
        test_set = []
        for test_sample, label in self._data_set.get_test_set():
            test_set.append((self._feature_extractor.get_features(test_sample), label))
        
        print 'Size of Test Set: ', len(test_set)
        print 'Accuracy on Test Set: %.2f' % (nltk.classify.accuracy(self._classifier, test_set) * 100.0)
        
    def most_informative_features(self, n = 10):
        return self._classifier.show_most_informative_features(n)
    
class ScikitClassifier(object):
    def __init__(self):
        self._data_set = NoSourceInfoDataset()#NoWhenDataset()#NoSourceAndNoHowInfoGotDataSet()#
        #preprocessor=lambda x:x.translate(const.TRANSLATE_TABLE), analyzer='word', ngram_range=(1, 1)
        #best_score:  0.849922030668
        #best_parameters:  {'clf__gamma': 0.0005, 'tfidf__use_idf': False, 'vect__ngram_range': (1, 2), 'clf__C': 1000.0, 'clf__kernel': 'rbf'}
        
        #################################################################
        #best_score:  0.854346068324
        #best_parameters:  {'vect__ngram_range': (1, 2), 'tfidf__use_idf': True}, these parameters were fixed: C=1000.0, kernel='rbf', gamma=0.0005, n_components=2000
        self._text_clf = Pipeline([('vect', CountVectorizer(preprocessor=lambda x:x.translate(const.TRANSLATE_TABLE), analyzer='word')),
                                   ('tfidf', TfidfTransformer()),
                                   #('pca', PCA()),
                                   ('clf', SVC(C=1000.0, kernel='rbf', gamma=0.0005))])
        print self._data_set.class_name_map
        
    @staticmethod
    def plot_1D(data, target, target_names):
        assert type(data) == np.ndarray
        assert type(target) == np.ndarray
        
        colors = ['w', 'black']
        pl.figure()
        n, bins, patches = pl.hist([data[target == 0], data[target == 1]], 2, histtype='bar',
                                   color=colors, range=[-0.5, 1.5], align='mid',
                                   label=[target_names[0], target_names[1]])
        pl.legend()
        pl.show()
    
    @staticmethod
    def hist_2D(data, target, feature_names, target_names):
        assert type(data) == np.ndarray
        assert type(target) == np.ndarray
        
        fig = plt.figure()
        
        x = data[target == 0][:, 0]
        y = data[target == 0][:, 1]
        H, xedges, yedges = np.histogram2d(x, y)
        extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
        ax1 = fig.add_subplot(1, 2, 1)
        plt.imshow(H, extent=extent, interpolation='nearest')
        plt.xlabel(feature_names[1])
        plt.ylabel(feature_names[0])
        plt.title(target_names[0])
        plt.set_cmap('gray')
        plt.colorbar(ax=ax1)
        
        x = data[target == 1][:, 0]
        y = data[target == 1][:, 1] 
        ax2 = fig.add_subplot(1, 2, 2)
        H, xedges, yedges = np.histogram2d(x, y)
        extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
        plt.imshow(H, extent=extent, interpolation='nearest')
        plt.xlabel(feature_names[1])
        plt.ylabel(feature_names[0])
        plt.title(target_names[1])
        plt.set_cmap('gray')
        plt.colorbar(ax=ax2)
        
        pl.show()
        
    @staticmethod
    def plot_2D(data, target, target_names, feature_names):
        assert type(data) == np.ndarray
        assert type(target) == np.ndarray
        
        colors = cycle('rgbcmykw')
        target_ids = range(len(target_names))
        pl.figure()
        for i, c, label in zip(target_ids, colors, target_names):
            #if i == 0: continue
            pl.scatter(data[target == i, 0], data[target == i, 1], c = c, label = label)
        
        plt.xlabel(feature_names[0])
        plt.ylabel(feature_names[1])    
        pl.legend()
        pl.show()
        
    @staticmethod
    def plot_3D(data, target, target_names):
        assert type(data) == np.ndarray
        assert type(target) == np.ndarray
        
        colors = cycle('rgbcmykw')
        target_ids = range(len(target_names))
        fig = pl.figure()
        ax = Axes3D(fig)
        for i, c, label in zip(target_ids, colors, target_names):
            ax.plot(data[target == i, 0], data[target == i, 1], data[target == i, 2], 'o', c = c, label = label)
            
        ax.legend()
        pl.show()
    
    @staticmethod
    def custom_tokenizer(txt):
        tokens = gutils.tokenize(txt)
        #stemmer = ISRIStemmer()
        #tokens = [stemmer.stem(token) for token in tokens]
        #tokens = [token[2:] if token.startswith(u'ال') else token for token in tokens]
        #tokens = [token[1:] if token.startswith(u'و') else token for token in tokens]
        tokens = [token for token in tokens if len(token) > 2]
        return tokens
        
    
    def __cross_validation(self, clf, X, y, raw_data, class_names):
        k_fold = cross_validation.KFold(len(X), n_folds = 5, indices = True)
        result = []
        k = 0
        for train, test in k_fold:
            cnt_wrong_pos = 0
            cnt_wrong_neg = 0
            k += 1
            clf.fit(X[train], y[train])
            predicted = clf.predict(X[test])
            fold_result = np.mean(predicted == y[test])
            result.append(fold_result)
            print "%.2f +ve, %.2f -ve" % ((len(y[test]) - np.count_nonzero(y[test])) * 100.0 / len(y[test]), np.count_nonzero(y[test]) * 100.0 / len(y[test]))
            print "Accuracy on Training Set: %.4f" % np.mean(clf.predict(X[train]) == y[train])
            print "Accuracy on Validation Set: %.4f" % fold_result
            print metrics.classification_report(y[test], predicted, target_names=self._data_set.class_name_map.keys())
            fold_analysis = []
            for j in xrange(0, len(test)):
                if predicted[j] == y[test[j]]: continue
                if y[test[j]] == 0: cnt_wrong_neg += 1
                else: cnt_wrong_pos += 1
                if y[test[j]] == 0: continue
                fold_analysis.append("Expected: {0}<-->Actual: {1}\nFeatures: {2}\n{3}\n".format(class_names[y[test[j]]], class_names[predicted[j]], X[test[j]],raw_data[test[j]]))
            helper.WRITE_FILE(os.path.join(const.ANALYSIS_LOG_DIR, "fold-{0}.log".format(k)),
                              "Accuracy: {0}\n{1}".format(fold_result, '\n'.join(fold_analysis)))
            print "Percentage incorrect of %s: %0.2f" % (class_names[1], cnt_wrong_neg * 1.0 / (cnt_wrong_neg + cnt_wrong_pos))
            print "Percentage incorrect of %s: %0.2f" % (class_names[0], cnt_wrong_pos * 1.0 / (cnt_wrong_neg + cnt_wrong_pos))
            
        print "K-Fold: ", result
        print "Average K-Fold: ", np.mean(result)
    
    def test_has_word(self):
        data = map(list, zip(* self._data_set.get_training_set() + self._data_set.get_validation_set()))
        X_train = data[0]
        y_train = np.array([self._data_set.class_name_map[y] for y in data[1]])
        print len(y_train)
        class_names = map(lambda (k,v): k, sorted(self._data_set.class_name_map.items(), key=lambda (k, v): v))
        
        fe = ScikitWordFeature(source_signal=False)
        X_train_words = fe.fit_transform(X_train)
        #X_train_words = preprocessing.normalize(X_train_words, norm='l2')
#        return X_train_words
        x_plot = X_train_words.toarray()
        ScikitClassifier.hist_2D(x_plot, y_train, fe.get_feature_names(), class_names)
        #ScikitClassifier.plot_2D(x_plot, y_train, class_names, fe.get_feature_names())
        #ScikitClassifier.plot_1D(x_plot, y_train, class_names)
        
        #clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, class_weight='auto', n_iter = 100)
        clf = LinearSVC(C=1.0, class_weight='auto', tol=1e-10, penalty='l2')
        self.__cross_validation(clf, x_plot, y_train, data[0], class_names)
        
        #k_fold = cross_validation.KFold(len(data[0]), n_folds = 5, indices = True)
        #result = [clf.fit(x_plot[train], y_train[train]).score(x_plot[test], y_train[test])
        #                for train, test in k_fold]
        #clf = clf.fit(X_train_words, y_train)
        #print "Cross Validation: ", result
        #print "Average: ", np.mean(result)
        
        #data = map(list, zip(* self._data_set.get_test_set()))
        #x_test = data[0]
        #y_test = np.array([self._data_set.class_name_map[y] for y in data[1]])
        #X_test_words = fe.transform(x_test)
        #predicted = clf.predict(X_test_words)
        #print 'Accuracy: %.2f' % (np.mean(predicted == y_test) * 100)
        #print metrics.classification_report(y_test, predicted, target_names=self._data_set.class_name_map.keys())
        
        #num = 0
        #for i in xrange(len(x_test)):
        #    if predicted[i] != y_test[i]:
        #        print x_test[i]
        #        print 'Expected: ', data[1][i]
        #        num += 1
        #    if num > 3:
        #        break
    
    def train_no_pipeline(self):
        data = map(list, zip(* self._data_set.get_training_set() + self._data_set.get_validation_set()))
        X_train = np.array(data[0])
        y_train = np.array([self._data_set.class_name_map[y] for y in data[1]])
        
        vect = CountVectorizer(preprocessor=lambda x: x.translate(const.TRANSLATE_TABLE), tokenizer = ScikitClassifier.custom_tokenizer, analyzer='word', ngram_range=(1,2), binary=True)
        x_train_counts = vect.fit_transform(X_train)
        
        tfidf = TfidfTransformer()
        x_train_tfidf = tfidf.fit_transform(x_train_counts)
        
        #tfidf = TfidfVectorizer(preprocessor=lambda x: x.translate(const.TRANSLATE_TABLE),
        #                        tokenizer = ScikitClassifier.custom_tokenizer,
        #                        analyzer='word', ngram_range=(1,2), binary=True)
        #x_train_tfidf = tfidf.fit_transform(X_train)
        pca = RandomizedPCA(n_components=3)
        plot_x = pca.fit_transform(x_train_tfidf)
        print type(x_train_tfidf)
        x_train_pca = x_train_tfidf#pca.fit_transform(x_train_tfidf)
        #print "Variance ratio: ", pca.explained_variance_ratio_
        #print "Total variance ratio: ", pca.explained_variance_ratio_.sum()
        
        #ch2 = SelectKBest(chi2, k = 3)
        #plot_x = np.array(ch2.fit_transform(x_train_pca, y_train).toarray())
        #ScikitClassifier.plot_3D(plot_x, y_train, self._data_set.class_name_map.keys())
        
        
        #ch2 = SelectKBest(chi2, k=4000)
        #x_train_pca = ch2.fit_transform(x_train_pca, y_train)
        
        #clf = SVC(C=1000.0, kernel='rbf', gamma=0.0005).fit(x_train_pca, y_train)
        #clf = MultinomialNB().fit(x_train_pca, y_train)
        clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=100, class_weight='auto')
        k_fold = cross_validation.KFold(len(data[0]), n_folds = 5, indices = True)
        #result = cross_validation.cross_val_score(clf, np.array(x_train_pca), np.array(y_train), cv=k_fold, n_jobs=1, verbose=2)
        result = [clf.fit(x_train_pca[train], y_train[train]).score(x_train_pca[test], y_train[test])
                        for train, test in k_fold]
        clf = clf.fit(x_train_pca, y_train)
        print "Cross Validation: ", result
        print "Average: ", np.mean(result)
        
        print "top 10 keywords per class:"
        feature_names = np.asarray(vect.get_feature_names())
        top10 = np.argsort(clf.coef_[0])[-30:]
        for feature_name, weight in zip(feature_names[top10], clf.coef_[0][top10]):
            print "%.2f\t%s" % (weight, feature_name)
        
        data = map(list, zip(* self._data_set.get_test_set()))
        x_test = np.array(data[0])
        y_test = np.array([self._data_set.class_name_map[y] for y in data[1]])
        x_test_counts = vect.transform(x_test)
        x_test_tfidf = tfidf.transform(x_test_counts)
        #x_test_tfidf = tfidf.transform(x_test)
        x_test_pca = x_test_tfidf#pca.transform(x_test_tfidf)
        #x_test_pca = ch2.transform(x_test_pca)
        predicted = clf.predict(x_test_pca)
        print 'Accuracy: %.2f' % (np.mean(predicted == y_test) * 100)
        print metrics.classification_report(y_test, predicted, target_names=self._data_set.class_name_map.keys())
        
    def feature_union(self, custom_test = False):
        data = map(list, zip(* self._data_set.get_training_set() + self._data_set.get_validation_set()))
        x_train = data[0]
        y_train = np.array([self._data_set.class_name_map[y] for y in data[1]])
        
        tfidf = TfidfVectorizer(preprocessor=lambda x: x.translate(const.TRANSLATE_TABLE),
                                tokenizer = ScikitClassifier.custom_tokenizer,
                                analyzer='word', ngram_range=(1,2), binary = False, use_idf=False)
        has_word = ScikitWordFeature(source_signal=True)
        union = FeatureUnion([("has_word", has_word), ("tfidf", tfidf)])
        x_train_union = union.fit_transform(x_train)
        
        x_train_union = preprocessing.normalize(x_train_union, norm='l2')
        #x_plot = x_train_union.toarray()
        #clf = MultinomialNB()
        #clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=100, class_weight='auto')
        clf = LinearSVC(C=1.0, penalty='l2')
        k_fold = cross_validation.KFold(len(data[0]), n_folds = 5, indices = True)
        result = [clf.fit(x_train_union[train, :], y_train[train]).score(x_train_union[test, :], y_train[test])
                        for train, test in k_fold]
        clf = clf.fit(x_train_union, y_train)
        print "Cross Validation: ", result
        print "Average: ", np.mean(result)
        
        print "top 10 keywords per class:"
        feature_names = np.asarray(union.get_feature_names())
        top10 = np.argsort(clf.coef_[0])[-40:]
        for feature_name, weight in zip(feature_names[top10], clf.coef_[0][top10]):
            print "%.2f\t%s" % (weight, feature_name)
            
        #top10 = np.argsort(clf.coef_[0])[:15]
        #for feature_name, weight in zip(feature_names[top10], clf.coef_[0][top10]):
        #    print "%.2f\t%s" % (weight, feature_name)
        
        data = map(list, zip(* self._data_set.get_test_set()))
        x_test = np.array(data[0])
        y_test = np.array([self._data_set.class_name_map[y] for y in data[1]])
        x_test_union = union.transform(x_test)
        x_test_union = preprocessing.normalize(x_test_union, norm='l2')
        predicted = clf.predict(x_test_union)
        print 'Accuracy: %.2f' % (np.mean(predicted == y_test) * 100)
        print '# of Incorrect: %d' % (len(data[0]) - np.count_nonzero(predicted == y_test))
        print '# of All: %d' % len(data[0])
        print metrics.classification_report(y_test, predicted, target_names=self._data_set.class_name_map.keys())
        
        if not custom_test: return
        for news_site in const.ALL_MCE_SOURCES:
            print '*******************************%s***************************' % news_site
            data = self._data_set.get_custom_test(news_site, 4)
            if len(data) == 0: continue
            data = map(list, zip(* data))
            x_test = np.array(data[0])
            y_test = np.array([self._data_set.class_name_map[y] for y in data[1]])
            x_test_union = union.transform(x_test)
            x_test_union = preprocessing.normalize(x_test_union, norm='l2')
            predicted = clf.predict(x_test_union)
            print 'Accuracy: %.2f' % (np.mean(predicted == y_test) * 100)
            print '# of Incorrect: %d' % (len(data[0]) - np.count_nonzero(predicted == y_test))
            print '# of All: %d' % len(data[0])
            print '# of violating: %d' % np.count_nonzero(predicted)
        
    def time_sfs(self):
        data = map(list, zip(* self._data_set.get_training_set() + self._data_set.get_validation_set()))
        x_train = data[0]
        y_train = np.array([self._data_set.class_name_map[y] for y in data[1]])
        
        week_days = [x.encode('utf-8') for x in [ u'الجمعة', u'السبت', u'الاحد', u'الاثنين',
                                                        u'الثلاثاء', u'الاربعاء', u'الخميس' ]]
        other_days = [x.encode('utf-8') for x in [u'اليوم', u'امس', u'منذ', u'قبل', u'غد', u'غدا', u'القادم', u'الماضي']]
        days = week_days + other_days
        for i in range(0, len(days)): print days[i], '\t',
        print ''
        best_days = []
        best_i = set()
        mx = 0 
        for i in range(0, len(days)):
            cur = 0
            cur_j = -1
            for j in range(0, len(days)):
                if j in best_i:
                    print '%s:--.--\t' % days[j], 
                    continue
                has_word = WhenFeatureDev(days=best_days + [days[j]])
                union = FeatureUnion([("has_word", has_word)])
                x_train_union = union.fit_transform(x_train)
                x_train_union = preprocessing.normalize(x_train_union, norm='l2')
                clf = LinearSVC(C=1.0, penalty='l2')
                k_fold = cross_validation.KFold(len(data[0]), n_folds = 5, indices = True)
                result = [clf.fit(x_train_union[train, :], y_train[train]).score(x_train_union[test, :], y_train[test])
                                for train, test in k_fold]
                clf = clf.fit(x_train_union, y_train)
                cur = np.mean(result)
                print '%s:%0.2f' % (days[j], cur * 100), '\t',
                if cur > mx:
                    mx = cur
                    cur_j = j
            if cur_j == -1: 
                break
            best_i.add(cur_j)
            best_days.append(days[cur_j])
            print ''
            print '+', days[cur_j], '-->', mx  
    
    def all_ngrams(self, idf=False, binary = False):
        best_dev_ij = (0, 0)
        best_dev = 0
        best_test_ij = (0, 0)
        best_test = 0
        for i in range(1, 6):
            for j in range(i, 6):
                data = map(list, zip(* self._data_set.get_training_set() + self._data_set.get_validation_set()))
                x_train = data[0]
                y_train = np.array([self._data_set.class_name_map[y] for y in data[1]])
                
                tfidf = TfidfVectorizer(#preprocessor=lambda x: x.translate(const.TRANSLATE_TABLE),
                                        tokenizer = ScikitClassifier.custom_tokenizer,
                                        analyzer='word', ngram_range=(i,j), binary = binary, use_idf=idf)
                union = FeatureUnion([("tfidf", tfidf)])
                x_train_union = union.fit_transform(x_train)
                
                print '%d, %d:\t' % (i, j),
                x_train_union = preprocessing.normalize(x_train_union, norm='l2')
                clf = LinearSVC(C=1.0, penalty='l2')
                k_fold = cross_validation.KFold(len(data[0]), n_folds = 5, indices = True)
                result = [clf.fit(x_train_union[train, :], y_train[train]).score(x_train_union[test, :], y_train[test])
                                for train, test in k_fold]
                clf = clf.fit(x_train_union, y_train)
                cur_dev = np.mean(result) * 100
                print "%0.2f\t" %cur_dev,
                if cur_dev > best_dev:
                    best_dev = cur_dev
                    best_dev_ij = (i, j)
                
                data = map(list, zip(* self._data_set.get_test_set()))
                x_test = np.array(data[0])
                y_test = np.array([self._data_set.class_name_map[y] for y in data[1]])
                x_test_union = union.transform(x_test)
                x_test_union = preprocessing.normalize(x_test_union, norm='l2')
                predicted = clf.predict(x_test_union)
                cur_test = np.mean(predicted == y_test) * 100
                print '%0.2f' % (cur_test)
                if cur_test > best_test:
                    best_test = cur_test
                    best_test_ij = (i, j)
                
        print "Best DEV: %0.2f --> (%d, %d)" % (best_dev, best_dev_ij[0], best_dev_ij[1])
        print "Best Test: %0.2f --> (%d, %d)" % (best_test, best_test_ij[0], best_test_ij[1])
        
    def train(self):
        data = map(list, zip(* self._data_set.get_training_set()))
        X_train = data[0]
        y_train = [self._data_set.class_name_map[y] for y in data[1]]
        print y_train[:10]
        param_grid = {#'clf__kernel': ['rbf', 'linear'],
                      #'vect__ngram_range': [(1, 1), (1, 2)],
                      #'tfidf__use_idf': (True, False),
                      'pca__n_components': [1000, 2000, 1500]}
        gs_clf = GridSearchCV(self._text_clf, param_grid, n_jobs=1)
        gs_clf = gs_clf.fit(X_train, np.array(y_train))
        print 'best_score: ', gs_clf.best_score_
        print 'best_parameters: ', gs_clf.best_params_
        return gs_clf
        #_ = self._text_clf.fit(X_train, y_train)
        
    def validation(self):
        data = map(list, zip(* self._data_set.get_validation_set()))
        X_test = data[0]
        y_test = [self._data_set.class_name_map[y] for y in data[1]]
        predicted = self._text_clf.predict(X_test)
        print 'Accuracy %.2f' % np.mean(predicted == y_test)
        print metrics.classification_report(y_test, predicted, target_names=self._data_set.class_name_map.keys())
        #print type(y_test)
        #print type(predicted)
        #print metrics.confusion_matrix(predicted, predicted)
        
    def cross_validation(self):
        data = map(list, zip(* self._data_set.get_training_set() + self._data_set.get_validation_set()))
        X_train = data[0]
        y_train = [self._data_set.class_name_map[y] for y in data[1]]
        print X_train
        k_fold = cross_validation.KFold(len(X_train), n_folds = 5, indices = True)
        result = cross_validation.cross_val_score(self._text_clf, X_train, y_train, cv=k_fold, n_jobs=1)
        print result
        print 'Average: ', np.mean(result)
        
        