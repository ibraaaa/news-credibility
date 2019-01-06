import random
import util.db as db
import util.helper as helper

class DataSet(object):
    def __init__(self, _db):
        self._db = _db
        self._pos_data = []
        self._neg_data = []
        self._training_set = []
        self._validation_set = []
        self._test_set = []
        self.class_name_map = {'credible':0}
        
        self._fraction_training_set = 0
        self._fraction_validation_set = 0
        self._fraction_test_set = 0
        for record in self._db.get_credible():
            self._pos_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'credible'))
        
        print 'Total Size of +ve Data: ', len(self._pos_data)
        
    def _divide_dataset(self):
        cnt_pos = self._fraction_training_set * len(self._pos_data) / 100
        cnt_neg = self._fraction_training_set * len(self._neg_data) / 100
        self._training_set = self._pos_data[:cnt_pos] + self._neg_data[:cnt_neg]
        
        random.seed(0)
        random.shuffle(self._training_set)
        print 'Size of Training Set: ', len(self._training_set), '\t ({0:.2f}% +ve, {1:.2f}% -ve)'.format(cnt_pos * 100.0 / len(self._training_set), cnt_neg * 100.0 / len(self._training_set))
        
        cnt_validation_pos = self._fraction_validation_set * len(self._pos_data) / 100
        cnt_validation_neg = self._fraction_validation_set * len(self._neg_data) / 100
        self._validation_set = self._pos_data[cnt_pos:cnt_pos + cnt_validation_pos] + self._neg_data[cnt_neg:cnt_neg + cnt_validation_neg]
        random.shuffle(self._validation_set)
        print 'Size of Validation Set: ', len(self._validation_set), '\t ({0:.2f}% +ve, {1:.2f}% -ve)'.format(cnt_validation_pos * 100.0 / len(self._validation_set), cnt_validation_neg * 100.0 / len(self._validation_set))
        print len(self._neg_data[:cnt_neg + cnt_validation_neg])
        self._test_set = self._pos_data[cnt_pos + cnt_validation_pos:] + self._neg_data[cnt_neg + cnt_validation_neg:]
        random.shuffle(self._test_set)
        print 'Size of Test Set: ', len(self._test_set), '\t ({0:.2f}% +ve, {1:.2f}% -ve)'.format((len(self._pos_data) - cnt_pos - cnt_validation_pos) * 100.0 / len(self._test_set), (len(self._neg_data) - cnt_neg - cnt_validation_neg) * 100.0 / len(self._test_set))
        print '------>Test Set Uniqueness test...'
        for i in self._test_set:
            assert i not in self._training_set
            assert i not in self._validation_set
        print 'Done'        

class NoSourceAndNoHowInfoGotDataSet(DataSet):
    def __init__(self, fraction_training_set = 65, fraction_validation_set = 15, fraction_test_set = 20):
        assert fraction_training_set + fraction_validation_set + fraction_test_set == 100
        DataSet.__init__(self, db.SourceSignalOperations())
        
        self._fraction_training_set = fraction_training_set
        self._fraction_validation_set = fraction_validation_set
        self._fraction_test_set = fraction_test_set
        self._training_set = []
        self._validation_set = []
        self._test_set = []
        
        self._neg_data = []
        self.class_name_map['no_source_info_AND_no_how_info_got'] = 1
        for record in self._db.get_no_source_info_and_no_how_info_got():
            self._neg_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'no_source_info_AND_no_how_info_got'))

        #random.shuffle(self._pos_data)
        #random.shuffle(self._neg_data)            
        print 'Total Size of -ve Data: ', len(self._neg_data)
        print 'Baseline: %.2f' % (max(len(self._neg_data), len(self._pos_data)) * 100.0 / (len(self._pos_data) + len(self._neg_data)))
            
    def get_training_set(self):
        if self._training_set: return self._training_set
        
        super(NoSourceAndNoHowInfoGotDataSet, self)._divide_dataset()
        return self._training_set
    
    def get_validation_set(self):
        assert len(self._validation_set) > 0
        return self._validation_set
    
    def get_test_set(self):
        assert len(self._test_set) > 0
        return self._test_set
    
class NoSourceInfoDataset(NoSourceAndNoHowInfoGotDataSet):
    def __init__(self, fraction_training_set = 65, fraction_validation_set = 15, fraction_test_set = 20):
        assert fraction_training_set + fraction_validation_set + fraction_test_set == 100
        
        self._fraction_training_set = fraction_training_set
        self._fraction_validation_set = fraction_validation_set
        self._fraction_test_set = fraction_test_set
        self._training_set = []
        self._validation_set = []
        self._test_set = []
        self._pos_data = []
        
        self._db = db.SourceSignalOperations()
        c = 1
        for record in self._db.get_credible():#self._db.get_uncredible_with_source_info():
            self._pos_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'has_source_info'))
            c += 1
            #if c > 1283: break;
        
        #for record in self._db.get_uncredible_with_source_info():
        #    self._pos_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'has_source_info'))
        #    c+=1
        #    if c > 2757: break
            
        self._neg_data = []
        self.class_name_map = {'has_source_info':0, 'no_source_info':1}
        for record in self._db.get_no_source_info():#self._db.get_no_how_info_got_or_no_source_info():#self._db.get_no_source_info_and_no_how_info_got():
            self._neg_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'no_source_info'))
            
        #random.shuffle(self._pos_data)
        #random.shuffle(self._neg_data)
        print 'Total Size of +ve Data: ', len(self._pos_data)
        print 'Total Size of -ve Data: ', len(self._neg_data)
        print 'Baseline: %.2f' % (max(len(self._neg_data), len(self._pos_data)) * 100.0 / (len(self._pos_data) + len(self._neg_data)))
        
    def get_custom_test(self, source, month):
        assert source
        assert month in range(1, 13)
        test = []
        for record in self._db.get_by_source_date_criteria(month, source, has_source=True):
            test.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'has_source_info'))
            
        for record in self._db.get_by_source_date_criteria(month, source, has_source=False):
            test.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'no_source_info'))
            
        return test                
    
class NoWhenDataset(DataSet):
    def __init__(self, fraction_training_set = 65, fraction_validation_set = 15, fraction_test_set = 20):        
        assert fraction_training_set + fraction_validation_set + fraction_test_set == 100
        #DataSet.__init__(self, db.SourceSignalOperations())
        self._db = db.SourceSignalOperations()
        
        self._fraction_training_set = fraction_training_set
        self._fraction_validation_set = fraction_validation_set
        self._fraction_test_set = fraction_test_set
        self._training_set = []
        self._validation_set = []
        self._test_set = []
        
        self._neg_data = []
        self._pos_data = []
        self.class_name_map = {'NoWhen': 0, 'HasWhen': 1 }
        
        for record in self._db.get_uncredible_with_when():
            self._pos_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'HasWhen'))
            
        for record in self._db.get_credible():
            self._pos_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'HasWhen'))
            
        for record in self._db.get_no_when():
            self._neg_data.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'NoWhen'))

        #random.shuffle(self._pos_data)
        #random.shuffle(self._neg_data)
        print 'Total Size of +ve Data: ', len(self._pos_data)            
        print 'Total Size of -ve Data: ', len(self._neg_data)
        print 'Baseline: %.2f' % (max(len(self._neg_data), len(self._pos_data)) * 100.0 / (len(self._pos_data) + len(self._neg_data)))
        
    def get_training_set(self):
        if self._training_set: return self._training_set
        
        super(NoWhenDataset, self)._divide_dataset()
        return self._training_set
    
    def get_validation_set(self):
        assert len(self._validation_set) > 0
        return self._validation_set
    
    def get_test_set(self):
        assert len(self._test_set) > 0
        return self._test_set
        
    def get_custom_test(self, source, month):
        assert source
        assert month in range(1, 13)
        test = []
        for record in self._db.get_by_source_date_criteria(month, source, answers_when=True):
            test.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'has_when'))
            
        for record in self._db.get_by_source_date_criteria(month, source, answers_when=False):
            test.append((helper.READ_FILE(helper.HTML_TO_TXT_DIR(record.news_html_filepath)), 'no_when'))
            
        return test    
        