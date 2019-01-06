#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import simplejson as json
import string
import util.const as CONST

def RSS_LABEL_TO_DIR(label_, is_html_):
    """Return the directory path to store URLs and HTML downloaded from RSS

       @param label_: the RSS label being crawled
       @param is_html_: True to return HTML directory and FALSE to return URLs directory
    """
    bottom_dir_ = '/'.join(label_.split('-'))
    ret_ = None
    if is_html_:
        ret_ = os.path.join(CONST.RSS_HTML_DIR, bottom_dir_)
    else:
        ret_ = os.path.join(CONST.RSS_URLS_DIR, bottom_dir_)

    if not os.path.exists(ret_): os.makedirs(ret_)

    return ret_

def FB_PAGE_TO_DIR(page_, is_html_):
    """Return the directory path to store URLs and HTML downloaded from FB

       @param page_: the FB page being crawled
       @param is_html_: True to return HTML directory and FALSE to return URLs directory
    """
    ret_ = None
    if is_html_:
        ret_ = os.path.join(CONST.FB_HTML_DIR, page_)
        if not os.path.exists(ret_): os.makedirs(ret_)
    else:
        ret_ = os.path.join(CONST.FB_URLS_DIR, page_)

    return ret_


def internal_read_file(file_name_, is_json_):
    f_ = open(file_name_, 'r')
    ret_ = f_.read()
    f_.close()

    if is_json_:
        return json.loads(ret_)
    return ret_

def READ_FIRST_LINE(file_name_):
    with open(file_name_, 'r') as f_:
        return f_.readline().decode('utf-8').strip(u'\n')


def READ_LINES(file_name_):
    with open(file_name_, 'r') as f_:
        ret = []
        for line in f_:
            ret.append(line.decode('utf-8').strip(u'\n'))
        return ret
        
def READ_FILE(file_name_):
    return internal_read_file(file_name_, False)

def READ_JSON_FILE(file_name_):
    return internal_read_file(file_name_, True)

def internal_write_file(file_name_, data_, mode_):
    f_ = open(file_name_, mode_)
    f_.write(data_)
    f_.close()

def WRITE_FILE(file_name_, data_):
    internal_write_file(file_name_, data_, 'w')

def WRITE_JSON_FILE(file_name_, data_, sort_keys_=False):
    internal_write_file(file_name_, json.dumps(data_, indent=2,
    sort_keys=sort_keys_), 'w')

def UPDATE_JSON_FILE(file_name_, key_, value_, sort_keys_=False):
    data_ = {}
    if os.path.exists(file_name_):
        data_ = READ_JSON_FILE(file_name_)
    data_[key_] = value_
    WRITE_JSON_FILE(file_name_, data_, sort_keys_)

def APPEND_TO_FILE(file_name_, data_):
    internal_write_file(file_name_, data_, 'a')

def HTML_TO_TXT_DIR(path_):
    txt_dir_ = os.path.dirname(path_).replace('html', 'txt')
    file_ = "{0}.txt".format(os.path.basename(path_)[:-5])
    return os.path.join(txt_dir_, file_)

def PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(txt):
    whitespace_table = dict([(ord(ch), None) for ch in string.whitespace])
    return txt.strip().translate(CONST.TRANSLATE_TABLE).translate(whitespace_table)
    
def NORMALIZE_TOKEN(token):
    token = token.translate(CONST.TRANSLATE_TABLE)
    token = token[2:] if token.startswith(u'ال') else token
    token = token[1:] if token.startswith(u'و') else token
    return token.encode('utf-8') if len(token) > 2 else None
    
class Logger:
    def __init__(self, log_dir_):
        self._log_dir = log_dir_

    def __log(self, text_, level_):
        if not os.path.exists(self._log_dir): os.makedirs(self._log_dir)
        f = open(os.path.join(self._log_dir, '{0}.log'.format(os.getpid())), 'a')
        f.write('{0}: {1}\n'.format(level_, text_))
        f.close()

    def log_info(self, text_):
        self.__log(text_, CONST.LOG_INFO_LEVEL)

    def log_error(self, msg_, stack_trace_):
        self.__log('{0}\n{1}\n'.format(msg_, stack_trace_), CONST.LOG_ERROR_LEVEL)

