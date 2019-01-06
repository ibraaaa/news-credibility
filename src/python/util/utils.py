#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import util.const as const
import util.db as db
import util.helper as helper

from datetime import datetime
from nltk.stem import ISRIStemmer

_db = db.IndexOperation()

def stem(word, stemmer):
    if not stemmer: return word.encode('utf-8')
    return stemmer.stem(word).encode('utf-8')
    #return subprocess.check_output(["php", "-f", "../lib/I18N/stem_word.php", word])

def get_verb(line, stemmer):
    line = line.translate(const.TRANSLATE_TABLE)
    for word in line.split(' '):
        if word and (ord(u'ت') == ord(word[0]) or ord(u'ي') == ord(word[0])):
            return stem(word.strip(), stemmer)
    return None

def get_all_verbs(start_date = datetime(1970, 1, 1), end_date = datetime(2013, 3, 11), stemmer=None):
    verbs = {}
    for label in const.RSS_POLITICS_LABELS:
        print label
        files = _db.select_filepath_by_label(label, start_date, end_date)
        for f in files:
            line = helper.READ_FIRST_LINE(helper.HTML_TO_TXT_DIR(f.file_path))
            verb = get_verb(line, stemmer)
            if not verb: continue
            if verb in verbs: verbs[verb] += 1
            else: verbs[verb] = 1
        sorted_verbs = sorted(verbs.items(), reverse = True, key = lambda k : k[1])
        helper.WRITE_FILE('../data/verbs_train.txt', '\n'.join("{0},{1}".format(k, v) for k, v in sorted_verbs))  
    
    print len(verbs)
        

def get_random_news_headlines(max_date = datetime(2013, 3, 11), count = 1000):
    ret = []
    for record in _db.select_random_records(const.RSS_POLITICS_LABELS, max_date, count):
        headline = helper.READ_FIRST_LINE(helper.HTML_TO_TXT_DIR(record.file_path))
        ret.append(u"{0},{1},{2}".format(record.file_path, record.url, headline))
        
    helper.WRITE_FILE('../data/headlines.txt', '\n'.join(ret).encode('utf-8'))