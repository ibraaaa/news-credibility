import os.path
import sys
import util.const as CONST
import util.helper as helper

from datetime import datetime
from peewee import BooleanField, IntegerField, ForeignKeyField
from peewee import CharField
from peewee import DateTimeField
from peewee import DoesNotExist
from peewee import Model
from peewee import MySQLDatabase
from peewee import TextField
from peewee import fn

custom_db = MySQLDatabase('news_index', user='ibraaaa', host='localhost', passwd='2441988')

class CustomModel(Model):
    class Meta:
        database = custom_db
    
class Index(CustomModel):
    file_path = TextField()
    url = TextField()
    date = DateTimeField()
    parsed = BooleanField()
    in_train = BooleanField()
    rss_label = CharField()
    news_site = CharField()
    
class IndexOperation(object):
    def create_table(self):
        Index.create_table()
        
    def __populate_from_json(self, label, json_data):
        news_site_ = label
        if '-' in label:
            news_site_ = label.split('-')[0]
        for k, v in json_data.items():
            # USE .exists instead: http://peewee.readthedocs.org/en/latest/peewee/api.html#SelectQuery
            #result = [entry for entry in Index.select().where(Index.file_path==k)]
            #if len(result) > 0: continue
            parsed_ = False
            if 'parsed' in v.keys():
                parsed_ = v['parsed']
            Index.create(file_path=k, url=v['url'], date=v['date'],
                        parsed=parsed_, in_train=False,
                        rss_label=label, news_site=news_site_)
            
    def populate_from_json(self, rss_labels=CONST.RSS_LABELS):            
        for label in rss_labels:
            self.__populate_from_json(label, helper.READ_JSON_FILE(os.path.join(CONST.RSS_HTML_INDEX_DIR, "{0}.json".format(label))))
            
    def create_entry(self, file_path, url, date, label, parsed=False, in_train=False):
        news_site_ = label
        if '-' in label:
            news_site_ = label.split('-')[0]
        Index.create(file_path = file_path, url = url, date = date,
                     rss_label = label, news_site = news_site_,
                     parsed = parsed, in_train = in_train)
        
    def get_path_by_url(self, url):
        try:
            return Index.get(Index.url == url).file_path
        except DoesNotExist:
            raise DBException("Url: '{0}' does not exist.".format(url)), None, sys.exc_info()[2]
        
    def get_date_by_path(self, file_path):
        try:
            return Index.get(Index.file_path == file_path).date
        except DoesNotExist:
            raise DBException("Path: '{0}' does not exist.".format(file_path)), None, sys.exc_info()[2]
        
    def select_unparsed_by_label(self, rss_label):
        return Index.select(Index.file_path).order_by(Index.date.asc()).where(
            (Index.parsed == False) & (Index.rss_label == rss_label))
    
    def select_filepath_by_label(self, rss_label, start_date = datetime(1970, 1, 1), end_date = datetime.now()):
        return Index.select(Index.file_path).order_by(Index.date.asc()).where(
            (Index.rss_label == rss_label) & (Index.date > start_date) & (Index.date < end_date))
    
    def set_parsed(self, file_path):
        return Index.update(parsed = True).where(Index.file_path == file_path).execute()
    
    def set_in_train(self, file_path):
        return Index.update(in_train = True).where(Index.file_path == file_path).execute()
    
    def select_by_rss_label(self, rss_label):
        return Index.select().where(
            (Index.rss_label == rss_label) & (Index.in_train == False) & (Index.parsed == True))
        
    def select_random_records(self, rss_labels, max_date = datetime(2013, 3, 11), limit = 1000):
        return Index.select(fn.Distinct(Index.file_path), Index.url).where((Index.rss_label << rss_labels) & (Index.date < max_date)).order_by(fn.Rand()).limit(limit)
    
    def get_by_url(self, url):
        try:
            return Index.get(Index.url == url)
        except DoesNotExist:
            return None
        
class MceWatchIndex(CustomModel):
    url = TextField()
    page = IntegerField()
    credible = BooleanField()
    parsed = BooleanField(default = False)

class MceWatchComplaint(CustomModel):
    mcewatch_index = ForeignKeyField(MceWatchIndex, related_name = "complaint")
    news_index = ForeignKeyField(Index, related_name = 'complaint', null = True)
    news_url = TextField()
    news_site = TextField(null = True)
    news_html_filepath = TextField(null = True)
    parsed_news_html = BooleanField(default = False)
    #mce_html_filepath = TextField()
    has_no_wrong_info = BooleanField(default = True)
    indicates_how_info_got = BooleanField(default = True)
    answers_why = BooleanField(default = True)
    no_misleading_title = BooleanField(default = True)
    no_misleading_video = BooleanField(default = True)
    correct_temporal_sequence = BooleanField(default = True)
    answers_how = BooleanField(default = True)
    no_sentiment_bias = BooleanField(default = True)
    answers_when = BooleanField(default = True)
    answers_where = BooleanField(default = True)
    no_incorrect_statistics = BooleanField(default = True)
    has_source_info = BooleanField(default = True)
    answers_who = BooleanField(default = True)
    no_incorrect_pics = BooleanField(default = True)
    old_posted_as_new = BooleanField(default = False)
    correct_news = BooleanField(default = True)
    expert_reasoning = TextField()
    ignore_row = BooleanField(default = False)
    month = IntegerField(null = True)
    

class MceWatchIndexOperation(object):
    def create_tables(self):
        if not MceWatchIndex.table_exists():
            MceWatchIndex.create_table()
            
        if not MceWatchComplaint.table_exists():
            MceWatchComplaint.create_table()
    
    def create_entry(self, urls, page, credible):
        with custom_db.transaction():
            for url in urls:
                MceWatchIndex.create(url=url, page=page, credible=credible, parsed = False)
    
    def select(self, page = None, credible = None):
        query = MceWatchIndex.select(MceWatchIndex.id, MceWatchIndex.url, MceWatchIndex.credible).where(MceWatchIndex.parsed == False)
        if page: query = query.where(MceWatchIndex.page == page)
        if credible is not None: query = query.where(MceWatchIndex.credible == credible)
        return query
    
    def __get_mce_complaints_page_by_id(self, complaint_id):
        return MceWatchIndex.get(MceWatchIndex.id == complaint_id)
    
    def create_complaint(self, complaints, news_url, news_site, expert_comments, mcewatch_page_id):
        new_complaint = MceWatchComplaint()
        new_complaint.mcewatch_index = self.__get_mce_complaints_page_by_id(mcewatch_page_id)
        #news_index = IndexOperation().get_by_url(news_url)
        #if news_index:
        #    new_complaint.news_html_filepath = news_index.file_path
        #    new_complaint.news_index = news_index
        #    new_complaint.parsed_news_html = True
        
        new_complaint.expert_reasoning = expert_comments
        new_complaint.news_url = news_url
        new_complaint.news_site = news_site
        
        for complaint in complaints:
            complaint = helper.PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(complaint)
            if complaint == CONST.MCE_WATCH_HAS_WRONG_INFO:
                new_complaint.has_no_wrong_info = False
            elif complaint == CONST.MCE_WATCH_NO_HOW_INFO_GOT:
                new_complaint.indicates_how_info_got = False
            elif complaint == CONST.MCE_WATCH_NO_ANSWER_WHY:
                new_complaint.answers_why = False
            elif complaint == CONST.MCE_WATCH_MISLEADING_TITLE:
                new_complaint.no_misleading_title = False
            elif complaint == CONST.MCE_WATCH_MISLEADING_VIDEO:
                new_complaint.no_misleading_video = False
            elif complaint == CONST.MCE_WATCH_WRONG_TEMPORAL_SEQUENCE:
                new_complaint.correct_temporal_sequence = False
            elif complaint == CONST.MCE_WATCH_NO_ANSWER_HOW:
                new_complaint.answers_how = False
            elif complaint == CONST.MCE_WATCH_BIASED:
                new_complaint.no_sentiment_bias = False
            elif complaint == CONST.MCE_WATCH_NO_ANSWER_WHEN:
                new_complaint.answers_when = False
            elif complaint == CONST.MCE_WATCH_NO_ANSWER_WHERE:
                new_complaint.answers_where = False
            elif complaint == CONST.MCE_WATCH_WRONG_STATISTICS:
                new_complaint.no_incorrect_pics = False
            elif complaint == CONST.MCE_WATCH_NO_SOURCE:
                new_complaint.has_source_info = False
            elif complaint == CONST.MCE_WATCH_NO_ANSWER_WHO:
                new_complaint.answers_who = False;
            elif complaint == CONST.MCE_WATCH_WRONG_PICS:
                new_complaint.no_incorrect_pics = False
            elif complaint == CONST.MCE_WATCH_OLD_POSTED_AS_NEW:
                new_complaint.old_posted_as_new = True
            elif complaint == CONST.MCE_WATCH_WRONG_NEWS:
                new_complaint.correct_news = False
                
        new_complaint.save()
        
    def get_news_urls_for_no_html(self, credible):
        return MceWatchComplaint.select(MceWatchComplaint.news_url, MceWatchComplaint.id).join(MceWatchIndex).where(
            (MceWatchComplaint.news_html_filepath >> None) &
            ~(MceWatchComplaint.news_site >> None) &
            (MceWatchIndex.credible == credible))
    
    def update_complaint_html_filepath(self, path, complaint_id):
        assert MceWatchComplaint.select().where((MceWatchComplaint.id == complaint_id) & (MceWatchComplaint.news_html_filepath >> None)).exists()
        MceWatchComplaint.update(news_html_filepath = path).where(MceWatchComplaint.id == complaint_id).execute()
        
    def get_unparsed_html(self, source):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath, MceWatchComplaint.id).where(
            (MceWatchComplaint.news_index >> None) &
            ~(MceWatchComplaint.news_html_filepath >> None) &
            (MceWatchComplaint.news_site == source) &
            (MceWatchComplaint.parsed_news_html == False) &
            (MceWatchComplaint.ignore_row == False))
        
    def set_news_html_parsed(self, complaint_id):
        assert MceWatchComplaint.select().where(MceWatchComplaint.id == complaint_id).exists()
        MceWatchComplaint.update(parsed_news_html = True).where(MceWatchComplaint.id == complaint_id).execute()
        assert MceWatchComplaint.select().where((MceWatchComplaint.id == complaint_id) & (MceWatchComplaint.parsed_news_html == True)).exists()
        
class SourceSignalOperations(object):
    def get_no_source_info_and_no_how_info_got(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
            (MceWatchComplaint.has_source_info == False) &
            (MceWatchComplaint.indicates_how_info_got == False) &
            (MceWatchComplaint.ignore_row == False))
    
    def get_credible(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).join(MceWatchIndex).where(
            ~(MceWatchComplaint.news_html_filepath >> None) & (MceWatchIndex.credible == True) & (MceWatchComplaint.ignore_row == False))
        
    def get_no_source_info(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
            (MceWatchComplaint.has_source_info == False) &
            (MceWatchComplaint.ignore_row == False))
        
    def get_no_how_info_got(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
            (MceWatchComplaint.indicates_how_info_got == False) &
            (MceWatchComplaint.ignore_row == False))
        
    def get_no_how_info_got_or_no_source_info(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
            ((MceWatchComplaint.has_source_info == False) |
            (MceWatchComplaint.indicates_how_info_got == False)) & (MceWatchComplaint.ignore_row == False))
        
    def get_uncredible_with_source_info(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).join(MceWatchIndex).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
             (MceWatchIndex.credible == False) &
             (MceWatchComplaint.has_source_info == True) &
             (MceWatchComplaint.indicates_how_info_got == True) &
            (MceWatchComplaint.ignore_row == False))
        
    def get_uncredible_with_when(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).join(MceWatchIndex).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
             (MceWatchIndex.credible == False) &
             (MceWatchComplaint.answers_when == True) &
            (MceWatchComplaint.ignore_row == False))
        
    def get_no_when(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(
            ~(MceWatchComplaint.news_html_filepath >> None) &
            (MceWatchComplaint.answers_when == False) &
            (MceWatchComplaint.ignore_row == False))
        
    def get_all(self):
        return MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(~(MceWatchComplaint.news_html_filepath >> None) & (MceWatchComplaint.ignore_row == False))
    
    def get_by_source_date_criteria(self, month = None, source = None, has_source = None, answers_when = None):
        query = MceWatchComplaint.select(MceWatchComplaint.news_html_filepath).where(~(MceWatchComplaint.news_html_filepath >> None) & (MceWatchComplaint.ignore_row == False))
        if month: query = query.where(MceWatchComplaint.month == month)
        if source: query = query.where(MceWatchComplaint.news_site == source)
        if has_source is not None: query = query.where(MceWatchComplaint.has_source_info == has_source)
        if answers_when is not None: query = query.where(MceWatchComplaint.answers_when == answers_when)
        return query
        
class DBException(Exception):
    pass
        
        