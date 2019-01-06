#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import string

DATA_DIR='../data'
LOG_DIR='../log'
RESOURCES_DIR='../../../../resources'

RSS_DIR=os.path.join(DATA_DIR, 'rss')
RSS_URLS_DIR=os.path.join(RSS_DIR, 'urls')
RSS_HTML_DIR=os.path.join(RSS_DIR, 'html')
RSS_HTML_INDEX_DIR=os.path.join(RSS_DIR, 'index')
RSS_LOG_DIR=os.path.join(LOG_DIR, 'rss')
LABEL_SINCE_FILE=os.path.join(RSS_URLS_DIR, 'label_since.json')


FB_DIR=os.path.join(DATA_DIR, 'fb')
FB_URLS_DIR=os.path.join(FB_DIR, 'urls')
FB_HTML_DIR=os.path.join(FB_DIR, 'html')
FB_HTML_INDEX_DIR=os.path.join(FB_DIR, 'index')
FB_LOG_DIR=os.path.join(LOG_DIR, 'fb')

HTML_PARSER_LOG_DIR=os.path.join(LOG_DIR, 'html_parser')

ARABIC_VERBS_FILE=os.path.join(RESOURCES_DIR, 'arabic_verbs.txt')
ENGLISH_VERBS_FILE=os.path.join(RESOURCES_DIR, 'english_verbs.txt')
SENTIWORDNET_FILE=os.path.join(RESOURCES_DIR, 'SentiWordNet_3.0.0_20130122.txt')

MCE = os.path.join(DATA_DIR, 'mce')
MCE_PAGES = os.path.join(MCE, 'pages')
MCE_PAGES_TRUSTED = os.path.join(MCE_PAGES, 'trusted')
MCE_PAGES_UNTRUSTED = os.path.join(MCE_PAGES, 'untrusted')

MCE_COMPLAINTS = os.path.join(MCE, 'complaints')
MCE_COMPLAINTS_TRUSTED = os.path.join(MCE_COMPLAINTS, 'trusted')
MCE_COMPLAINTS_UNTRUSTED = os.path.join(MCE_COMPLAINTS, 'untrusted')

NEWS_HTML_BY_MCE = os.path.join(MCE, 'html')
TRUSTED_NEWS_HTML_BY_MCE = os.path.join(NEWS_HTML_BY_MCE, 'trusted')
UNTRUSTED_NEWS_HTML_BY_MCE = os.path.join(NEWS_HTML_BY_MCE, 'untrusted')

ANALYSIS_LOG_DIR = os.path.join(LOG_DIR, 'analysis')

# Log levels
LOG_INFO_LEVEL = 'INFO'
LOG_ERROR_LEVEL = 'ERROR'

# News sites names
AHRAM='Alahram.Newspaper'
AKHBAR='akhbarelyomgate'
ALMASRY_ELYOM='almasryalyoum'
BBC_ARABIC='bbcarabicnews'
CNN_ARABIC='cnnarabic'
DOSTOR='aldostornews'
DOSTOR_ASLY='El.Dostor.News'
FAGR='elfagr'
MASRAWY='masrawy'
SHOROUK='shorouknews'
TAHRIR='Tahrir.News.Official'
WATAN='ElWatanNews'
YOUM7='officialyoum77'
# NOT IN FB
#HURRYH='hurryh'
FJP='fjp'
ENGLISH_FJP='englishFjp'
ENGLISH_AHRAM='englishAhram'
# supported by MCE Watch
AKHBAR_MASR='akhbarmasr'
RASD='rasd'
MASRYOON='almasryoon'
WAFD='alwafd'
AKHBAR_ELYOM='akhbarelyom'
BADIL='elbadil'

EXTRA_MCE_SOURCES = [AKHBAR_MASR, RASD, MASRYOON, WAFD, AKHBAR_ELYOM, BADIL, DOSTOR, AHRAM]
ALL_MCE_SOURCES = EXTRA_MCE_SOURCES + [ALMASRY_ELYOM, SHOROUK, FJP, DOSTOR_ASLY, YOUM7, MASRAWY, TAHRIR, WATAN, FAGR]

# News feeds tags
ACCIDENTS='accidents'
ALL='all'
ARTICLES='articles'
CASES='cases'
EGYPT='egypt'
INVESTIGATIONS='investigations'
LATEST='latest'
MIDEAST='mideast'
POLITICS='politics'
WORLD='world'

# Classified news tags
AHRAM_ACCIDENTS='{0}-{1}'.format(AHRAM, ACCIDENTS)
AHRAM_CASES='{0}-{1}'.format(AHRAM, CASES)
AHRAM_EGYPT='{0}-{1}'.format(AHRAM, EGYPT)
AHRAM_INVESTIGATIONS='{0}-{1}'.format(AHRAM, INVESTIGATIONS)
AHRAM_POLITICS='{0}-{1}'.format(AHRAM, POLITICS)
ALMASRY_ELYOM_ACCIDENTS='{0}-{1}'.format(ALMASRY_ELYOM, ACCIDENTS)
ALMASRY_ELYOM_EGYPT='{0}-{1}'.format(ALMASRY_ELYOM, EGYPT)
ALMASRY_ELYOM_INVESTIGATIONS='{0}-{1}'.format(ALMASRY_ELYOM, INVESTIGATIONS)
CNN_ARABIC_LATEST='{0}-{1}'.format(CNN_ARABIC, LATEST)
CNN_ARABIC_MIDEAST='{0}-{1}'.format(CNN_ARABIC, MIDEAST)
CNN_ARABIC_WORLD='{0}-{1}'.format(CNN_ARABIC, WORLD)
DOSTOR_ASLY_ACCIDENTS='{0}-{1}'.format(DOSTOR_ASLY, ACCIDENTS)
DOSTOR_ASLY_ALL='{0}-{1}'.format(DOSTOR_ASLY, ALL)
DOSTOR_ASLY_POLITICS='{0}-{1}'.format(DOSTOR_ASLY, POLITICS)
ENGLISH_AHRAM_ALL='{0}-{1}'.format(ENGLISH_AHRAM, ALL)
ENGLISH_AHRAM_EGYPT='{0}-{1}'.format(ENGLISH_AHRAM, EGYPT)
ENGLISH_AHRAM_WORLD='{0}-{1}'.format(ENGLISH_AHRAM, WORLD)
FAGR_ACCIDENTS='{0}-{1}'.format(FAGR, ACCIDENTS)
FAGR_EGYPT='{0}-{1}'.format(FAGR, EGYPT)
#FAGR_LATEST='{0}-{1}'.format(FAGR, LATEST)
FAGR_WORLD='{0}-{1}'.format(FAGR, WORLD)
FJP_ALL='{0}-{1}'.format(FJP, ALL)
FJP_ARTICLES='{0}-{1}'.format(FJP, ARTICLES)
FJP_INVESTIGATIONS='{0}-{1}'.format(FJP, INVESTIGATIONS)
FJP_MIDEAST='{0}-{1}'.format(FJP, MIDEAST)
MASRAWY_ACCIDENTS='{0}-{1}'.format(MASRAWY, ACCIDENTS)
MASRAWY_MIDEAST='{0}-{1}'.format(MASRAWY, MIDEAST)
MASRAWY_POLITICS='{0}-{1}'.format(MASRAWY, POLITICS)
MASRAWY_WORLD='{0}-{1}'.format(MASRAWY, WORLD)
SHOROUK_ACCIDENTS='{0}-{1}'.format(SHOROUK, ACCIDENTS)
SHOROUK_MIDEAST='{0}-{1}'.format(SHOROUK, MIDEAST)
SHOROUK_POLITICS='{0}-{1}'.format(SHOROUK, POLITICS)
SHOROUK_WORLD='{0}-{1}'.format(SHOROUK, WORLD)
WATAN_ACCIDENTS='{0}-{1}'.format(WATAN, ACCIDENTS)
WATAN_INVESTIGATIONS='{0}-{1}'.format(WATAN, INVESTIGATIONS)
WATAN_LATEST='{0}-{1}'.format(WATAN, LATEST)
WATAN_POLITICS='{0}-{1}'.format(WATAN, POLITICS)
YOUM7_ACCIDENTS='{0}-{1}'.format(YOUM7, ACCIDENTS)
YOUM7_ARTICLES='{0}-{1}'.format(YOUM7, ARTICLES)
YOUM7_LATEST='{0}-{1}'.format(YOUM7, LATEST)

#DOSTOR website is usually down!
#HURRYUH is no longer supported
#ELFAGR-LATEST doesn't send feeds!
#AHRAM removed support for RSS!
RSS_LABELS=[AKHBAR, #AHRAM_EGYPT, AHRAM_INVESTIGATIONS,
            #AHRAM_POLITICS, AHRAM_ACCIDENTS, AHRAM_CASES,
            ALMASRY_ELYOM_ACCIDENTS,
            ALMASRY_ELYOM_EGYPT, ALMASRY_ELYOM_INVESTIGATIONS,
            BBC_ARABIC, CNN_ARABIC_LATEST, CNN_ARABIC_MIDEAST,
            CNN_ARABIC_WORLD, DOSTOR_ASLY_ACCIDENTS,
            DOSTOR_ASLY_ALL, DOSTOR_ASLY_POLITICS,
            ENGLISH_AHRAM_ALL, ENGLISH_AHRAM_EGYPT,
            ENGLISH_AHRAM_WORLD, ENGLISH_FJP, FAGR_ACCIDENTS,
            FAGR_EGYPT, FAGR_WORLD, WATAN_ACCIDENTS, FJP_ALL,
            FJP_ARTICLES, FJP_INVESTIGATIONS,FJP_MIDEAST,
            WATAN_INVESTIGATIONS, WATAN_LATEST, WATAN_POLITICS,
            MASRAWY_ACCIDENTS, MASRAWY_MIDEAST, MASRAWY_POLITICS,
            MASRAWY_WORLD, YOUM7_ACCIDENTS, YOUM7_ARTICLES,
            YOUM7_LATEST, SHOROUK_ACCIDENTS, SHOROUK_MIDEAST,
            SHOROUK_POLITICS, SHOROUK_WORLD, TAHRIR]

RSS_POLITICS_LABELS=[AKHBAR, ALMASRY_ELYOM_EGYPT, BBC_ARABIC,
                     CNN_ARABIC_MIDEAST, DOSTOR_ASLY_POLITICS,
                     FAGR_EGYPT, FJP_ALL, WATAN_POLITICS,
                     MASRAWY_POLITICS, YOUM7_LATEST,
                     SHOROUK_POLITICS, TAHRIR]

FB_PAGES=[AHRAM, AKHBAR, ALMASRY_ELYOM, BBC_ARABIC, CNN_ARABIC,
          DOSTOR, DOSTOR_ASLY, FAGR, SHOROUK, TAHRIR, WATAN,
          YOUM7]

TRANSLATE_TABLE = dict((ord(ch), None) for ch in string.punctuation + string.digits)
TRANSLATE_TABLE[ord(u'أ')] = ord(u'ا')
TRANSLATE_TABLE[ord(u'آ')] = ord(u'ا')
TRANSLATE_TABLE[ord(u'إ')] = ord(u'ا')
TRANSLATE_TABLE[ord(u'ى')] = ord(u'ي')
#TRANSLATE_TABLE[ord(u'ؤ')] = ord(u'ء')
#TRANSLATE_TABLE[ord(u'ئ')] = ord(u'ء')
#TRANSLATE_TABLE[ord(u'ة')] = ord(u'ه')
TRANSLATE_TABLE[ord(u'ْ')] = None
TRANSLATE_TABLE[ord(u'ُ')] = None
TRANSLATE_TABLE[ord(u'`')] = None
TRANSLATE_TABLE[ord(u'ٌ')] = None
TRANSLATE_TABLE[ord(u'ً')] = None
TRANSLATE_TABLE[ord(u'َ')] = None
TRANSLATE_TABLE[ord(u'؛')] = None
TRANSLATE_TABLE[ord(u'~')] = None
TRANSLATE_TABLE[ord(u'ِ')] = None
TRANSLATE_TABLE[ord(u'ـ')] = None
TRANSLATE_TABLE[ord(u'،')] = None
TRANSLATE_TABLE[ord(u'؟')] = None
TRANSLATE_TABLE[ord(u'¦')] = None
TRANSLATE_TABLE[ord(u'»')] = None
TRANSLATE_TABLE[ord(u'«')] = None
TRANSLATE_TABLE[ord(u'”')] = None
TRANSLATE_TABLE[ord(u'“')] = None


def PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(txt):
    whitespace_table = dict([(ord(ch), None) for ch in string.whitespace])
    return txt.strip().translate(TRANSLATE_TABLE).translate(whitespace_table)

MCE_WATCH_HAS_WRONG_INFO = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر يحتوي على معلومات خاطئة او مغلوطة أو ناقصة (1 درجات)')
MCE_WATCH_NO_HOW_INFO_GOT = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر لا يشير الى كيفية الحصول على المعلومة (0.5 درجات)')
MCE_WATCH_NO_ANSWER_WHY = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر لا يُجيب على سؤال “لماذا” ؟ (0.5 درجات)')
MCE_WATCH_MISLEADING_TITLE = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر يحتوي عنوان مخالف للنص (2 درجات)')
MCE_WATCH_MISLEADING_VIDEO = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الفيديو مخالف او متعارض مع نص الخبر (2 درجات)')
MCE_WATCH_WRONG_TEMPORAL_SEQUENCE = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'التسلسل الزمني للخبر غير سليم (2 درجات)')
MCE_WATCH_NO_ANSWER_HOW = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر لا يُجيب على سؤال “كيف” ؟ (0.5 درجات)')
MCE_WATCH_BIASED = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر غير حيادي ومنحاز (2 درجات)')
MCE_WATCH_NO_ANSWER_WHEN = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر لا يُجيب على سؤال “متى”؟ (1 درجات)')
MCE_WATCH_NO_ANSWER_WHERE = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر لا يُجيب على سؤال “أين” ؟ (1 درجات)')
MCE_WATCH_WRONG_STATISTICS = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر يحتوي على ارقام او بيانات او احصائيات غير دقيقة (2 درجات)')
MCE_WATCH_NO_SOURCE = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر لا يشير الى هوية المصدر (2 درجات)')
MCE_WATCH_NO_ANSWER_WHO = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبرلا يُجيب على سؤال “من” ؟ (4 درجات)')
MCE_WATCH_WRONG_PICS = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبر يحتوي على صور غير سليمة او تم التلاعب بها (1 درجات)')
MCE_WATCH_OLD_POSTED_AS_NEW = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'خبر قديم نشر على انه خير جديد (3 درجات)')
MCE_WATCH_WRONG_NEWS = PREPROCESS_MCE_WATCH_JUDGE_CRITERIA(u'الخبرغير صحيح ! (6 درجات)')

MCE_WATCH_JUDGMENT_CRITERIA = [MCE_WATCH_HAS_WRONG_INFO,
                               MCE_WATCH_NO_HOW_INFO_GOT,
                               MCE_WATCH_NO_ANSWER_WHY,
                               MCE_WATCH_MISLEADING_TITLE,
                               MCE_WATCH_MISLEADING_VIDEO,
                               MCE_WATCH_WRONG_TEMPORAL_SEQUENCE,
                               MCE_WATCH_NO_ANSWER_HOW,
                               MCE_WATCH_BIASED,
                               MCE_WATCH_NO_ANSWER_WHEN,
                               MCE_WATCH_NO_ANSWER_WHERE,
                               MCE_WATCH_WRONG_STATISTICS,
                               MCE_WATCH_NO_SOURCE,
                               MCE_WATCH_NO_ANSWER_WHO,
                               MCE_WATCH_WRONG_PICS,
                               MCE_WATCH_OLD_POSTED_AS_NEW,
                               MCE_WATCH_WRONG_NEWS]

MCE_WATCH_SOURCES_MAPPING = {u'اخبار مصر': AKHBAR_MASR,
                             u'masrawy': MASRAWY,
                             u'egypt': ALMASRY_ELYOM,
                             u'رصد': RASD,
                             u'المصريون': MASRYOON,
                             u'الحرية و العدالة': FJP,
                             u'الشروق': SHOROUK,
                             u'الوفد': WAFD,
                             u'اخبار اليوم': AKHBAR_ELYOM,
                             u'التحرير': TAHRIR,
                             u'الدستور الاصلي': DOSTOR_ASLY,
                             u'اليوم السابع': YOUM7,
                             u'البديل': BADIL,
                             u'new dostor': DOSTOR,
                             u'الوطن': WATAN,
                             u'1094': AHRAM,
                             u'الفجر': FAGR}

BUCKWALTER_TO_UNICODE = {36: u'\u0634',
                         38: u'\u0624',
                         39: u'\u0621',
                         42: u'\u0630',
                         60: u'\u0625',
                         62: u'\u0623',
                         65: u'\u0627',
                         68: u'\u0636',
                         69: u'\u0639',
                         70: u'\u064b',
                         72: u'\u062d',
                         75: u'\u064d',
                         78: u'\u064c',
                         83: u'\u0635',
                         84: u'\u0637',
                         89: u'\u0649',
                         90: u'\u0638',
                         95: u'\u0640',
                         96: u'\u0670',
                         97: u'\u064e',
                         98: u'\u0628',
                         100: u'\u062f',
                         102: u'\u0641',
                         103: u'\u063a',
                         104: u'\u0647',
                         105: u'\u0650',
                         106: u'\u062c',
                         107: u'\u0643',
                         108: u'\u0644',
                         109: u'\u0645',
                         110: u'\u0646',
                         111: u'\u0652',
                         112: u'\u0629',
                         113: u'\u0642',
                         114: u'\u0631',
                         115: u'\u0633',
                         116: u'\u062a',
                         117: u'\u064f',
                         118: u'\u062b',
                         119: u'\u0648',
                         120: u'\u062e',
                         121: u'\u064a',
                         122: u'\u0632',
                         123: u'\u0671',
                         124: u'\u0622',
                         125: u'\u0626',
                         126: u'\u0651'}

UNICODE_TO_BUCKWALTER = {1569: 39,
                         1570: 124,
                         1571: 62,
                         1572: 38,
                         1573: 60,
                         1574: 125,
                         1575: 65,
                         1576: 98,
                         1577: 112,
                         1578: 116,
                         1579: 118,
                         1580: 106,
                         1581: 72,
                         1582: 120,
                         1583: 100,
                         1584: 42,
                         1585: 114,
                         1586: 122,
                         1587: 115,
                         1588: 36,
                         1589: 83,
                         1590: 68,
                         1591: 84,
                         1592: 90,
                         1593: 69,
                         1594: 103,
                         1600: 95,
                         1601: 102,
                         1602: 113,
                         1603: 107,
                         1604: 108,
                         1605: 109,
                         1606: 110,
                         1607: 104,
                         1608: 119,
                         1609: 89,
                         1610: 121,
                         1611: 70,
                         1612: 78,
                         1613: 75,
                         1614: 97,
                         1615: 117,
                         1616: 105,
                         1617: 126,
                         1618: 111,
                         1648: 96,
                         1649: 123}