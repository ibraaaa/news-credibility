#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.html
import os.path
import threading
import traceback
import util.const as CONST
import util.db as db
import util.helper as helper
from multiprocessing import Pool


class HTMLParser(object):
    def __parse_shorouk(self, html_):
        page_ = lxml.html.fromstring(html_)
        title_ = page_.find_class('right')
        data_ = []
        # Get article title.
        for x in title_:
            text_nodes_ = x.xpath('h1/child::text() | h3/child::text()')
            title_text_ = ''
            for text_node_ in text_nodes_:
                if text_node_:
                    title_text_ += text_node_.encode('utf-8').lstrip() + ' '

            if title_text_: data_.append(title_text_)

        #CHECK: ../data/rss/html/shorouknews/accidents/67/2013-02-21%2020:10:00%2367a7c33d-ace1-4fa9-aa3c-a227a53714ec.html
        # Fixed manual for now
        body_ = page_.find_class('rightContent-newSize') 
        # Get article body.
        for x in body_:
            text_nodes_ = x.xpath('p/descendant::text()')
            for text_node_ in text_nodes_:
                if text_node_:
                    data_.append(text_node_.encode('utf-8'))


        # helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_cnn_arabic(self, html_):
        page_ = lxml.html.fromstring(html_)
        title_ = page_.xpath("//div[@class='cnn_storyarea']/h1/child::text()")
        data_ = []
        for text_ in title_:
            if text_: data_.append(text_.encode('utf-8'))

        body_ = page_.xpath("//div[@class='cnn_strycntntrgt']/p/descendant::text()")
        for text_ in body_:
            if text_: data_.append(text_.encode('utf-8'))
        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_akhbarelyomgate(self, html_):
        """Parses HTML from 'Akhbar El-Yom'. Articles are laid out in tables.
           Article title can be found near by an element with CSS class name
           'articleTitle', we get this and then go up one step typically to
           the parent row including the element with this CSS class and then
           get all text nodes in the descendants

           Similar approach is done for the article body but the CSS class is
           'articleBody'
        """
        page_ = lxml.html.fromstring(html_)
        elements_ = page_.find_class('articleTitle')
        data_ = []
        for e in elements_:
            title_ = e.xpath('parent::node()/descendant::text()')
            for text_ in title_:
                text_ = text_.encode('utf-8').strip()
                if text_: data_.append(text_)
            break;

        elements_ = page_.find_class('articleBody')
        for e in elements_:
            body_ = e.xpath('parent::node()/descendant::text()')
            for text_ in body_:
                text_ = text_.encode('utf-8').strip()
                if text_: data_.append(text_)
            break;
            
        return '\n'.join(data_)

    def __parse_almasryalyoum(self, html_):
        page_ = lxml.html.fromstring(html_)
        elements_ = page_.find_class('custom-article-title')
        data_ = []
        for e in elements_:
            title_ = e.xpath('descendant-or-self::text()')
            for text_ in title_:
                text_ = text_.encode('utf-8').strip()
                if text_: data_.append(text_)

        #elements_ = page_.find_class('panel-pane pane-node-body')
        #for e in elements_:
        #    body_ = e.xpath("descendant-or-self::text()")
        #    for text_ in body_:
        #        text_ = text_.encode('utf-8').strip()
        #        if text_: data_.append(text_)
        body_ = page_.xpath("//div[@class='panel-pane pane-node-body']/div[@class='pane-content']/div | //div[@class='panel-pane pane-node-body']/div[@class='pane-content']/p")
        for b in body_:
            ignore = False
            for attribute in b.xpath("@*"):
                if 'embeded-read-also' in attribute:
                    ignore = True
            if ignore: continue
            data_.extend([t.encode('utf-8').strip() for t in b.xpath("descendant-or-self::text()") if t])
        
        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_elfagr(self, html_):
        page_ = lxml.html.fromstring(html_)
        elements_ = page_.get_element_by_id("ctl00_ContentPlaceHolder1_maintd")
        if not elements_: elements_ = page_.find_class('DetailsPageContent')  # the check seems wrong
        data_ = []
        for e in elements_:
            text_ = e.text_content().encode('utf-8').strip()
            if text_ and text_[-2:] != 'PM' and text_[-2:] != 'AM': data_.append(text_)
        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_english_ahram(self, html_):
        page_ = lxml.html.fromstring(html_)
        exp = "//div[@id='ctl00_ContentPlaceHolder1_divLeftTitle']";
        # Title
        elements_ = page_.xpath(exp + "/div[@id='ctl00_ContentPlaceHolder1_hd']/descendant::text()")
        # Brief
        elements_.extend(page_.xpath(exp + "/div[@id='ctl00_ContentPlaceHolder1_bref']/descendant::text()"))
        data_ = []
        for e in elements_:
            e = e.encode('utf-8').strip()
            if e: data_.append(e)

        exp = "//div[@id='ctl00_ContentPlaceHolder1_divContent']/"
        elements_ = page_.xpath(exp + "child::text()")
        elements_.extend(page_.xpath(exp + "p/descendant::text()"))

        for e in elements_:
            e = e.encode('utf-8').strip()
            if "short link:" in e.lower(): continue
            if e: data_.append(e)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_fjp(self, html_):
        page_ = lxml.html.fromstring(html_)
        title_ = page_.xpath("//div[@id='PressRTitles']/descendant::text()")
        data_ = []
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        body_ = page_.xpath("//div[@id='PressRContent']/p/descendant::text()")
        body_.extend(page_.xpath("//div[@id='PressRContent']/child::text()")) # Added recently
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
        
        # Add text from all div elements except those with attribute named 'PressRDateAdded' or 'fonts',
        # which correspond to the date and author, respectively.
        body_ = page_.xpath("//div[@id='PressRContent']/div")
        for node in body_:
            ignore = False
            for attribute in node.xpath("@*"):
                if 'PressRDateAdded' in attribute or 'fonts' in attribute:
                    ignore = True
                    break
            if ignore: continue
            data_.extend([t.encode('utf-8').strip() for t in node.xpath("descendant-or-self::text()") if t])
        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_masrawy(self, html_):
        page_ = lxml.html.fromstring(html_)
        title_ = page_.xpath("//div[@id='mclip']/div[@id='artical']/h1/descendant::text()")
        data_ = []
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        body_ = page_.xpath("//div[@id='mclip']/div[@id='artical']/div[@id='content']/child::text()") #Added recently
        body_.extend(page_.xpath("//div[@id='mclip']/div[@id='artical']/div[@id='content']/p/descendant::text()"))
        for b in body_:
            b = b.encode('utf-8').strip()
            #print b
            # Break if the text "2kra2 2ydan:"
            if u'\u0627\u0642\u0631\u0623 \u0623\u064A\u0636\u0627:'.encode('utf-8') in b: break
            if b: data_.append(b)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_ahram(self, html_): # AHRAM update this site, this is not used anymore, only for old data.
        page_ = lxml.html.fromstring(html_)
        exp = "//div[@id='ArticlePrintVersion']/div[@class='bbbody']/"
        title_ = page_.xpath(exp + "div[@id='headDiv']/div[@id='divtitle']/span[@id='txtTitle']/descendant::text()")
        data_ = []
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        body_ = page_.xpath(exp + "div[@id='abstractDiv']/descendant::text()")
        body_.extend(page_.xpath(exp + "descendant-or-self::node()/div[@id='bodyDiv']/descendant::text()"))

        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)
    
    def __parse_ahram_NEW_SITE(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@id='ctl00_ContentPlaceHolder1_divTitle']/descendant::text()")
        title_.extend(page_.xpath("//div[@id='ctl00_ContentPlaceHolder1_hd']/descendant::text()"))
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@id='ctl00_ContentPlaceHolder1_divContent']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b and not u'رابط دائم'.encode('utf-8') in b: data_.append(b)
        
        return '\n'.join(data_)
    
    def __parse_bbcarabic(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        exp = "//div[@class=' g-w20 g-first']/div[@class='g-container']/h1/descendant-or-self::text()"
        for t in page_.xpath(exp):
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        exp = "//div[@class=' g-w20 g-first']/div[@class='g-container story-body']/div[@class='bodytext']/p/descendant::text() | "
        exp += "//div[@class=' g-w20 g-first']/div[@class='g-container']/div[@class='bodytext']/p/descendant::text()"
        for t in page_.xpath(exp):
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
        #for node in page_.xpath(exp):
            #if node.xpath("attribute::class") == "module inline-contextual-links":
            #    continue
        #    text_ = node.xpath("descendant-or-self::text()")
        #    for t in text_:
        #        t = t.encode('utf-8').strip()
        #        if t: data_.append(t)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_dostorasly(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        exp = "//div[@class='contentMain']/div[@class='rightArea']/"
        title_ = page_.xpath(exp + "div[@class='sectionTitle']/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        body_ = page_.xpath(exp + "div[@class='authorArticleContent']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_elwatannews(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        exp = "//div[@class='main_content_ip']/h1[@class='article_title']/descendant-or-self::text()"
        title_ = page_.xpath(exp)
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        exp = "//div[@class='main_content_ip']/span[@class='SubTitle']/descendant::text()"
        exp += " | //div[@class='main_content_ip']/p/descendant::text()"
        body_ = page_.xpath(exp)
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_english_fjp(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        exp = "//div[@id='leftcontent']/table"
        title_ = page_.xpath(exp + "/tr[3]/td/div/child::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        body_ = page_.xpath(exp + "/tr[7]/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_youm7(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        exp = "//div[@id='newsStory']/div[@id='newsStoryHeader']/"
        title_ = page_.xpath(exp + 'h1/descendant::text() | ' + exp + 'h2/descendant::text() | ' + exp + 'h3/descendant::text()')
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        exp = "//div[@id='newsStory']/div[@id='newsStoryContent']/div[@id='newsStoryTxt']/p/descendant::text()" #changed child to descendant
        body_ = page_.xpath(exp)
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)

        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        return '\n'.join(data_)

    def __parse_tahrir(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@class='eventTitle']/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)

        body_ = page_.xpath("//div[@class='eventInner']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)

        return '\n'.join(data_)
        #helper.WRITE_FILE('/home/ibraaaa/Desktop/test_1.txt', '\n'.join(data_))
        
    def __parse_akhbar_masr(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@class='content-header tr']/h2/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@class='main-section user-content']/p/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
        
        return '\n'.join(data_)
    
    def __parse_rasd(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@class='page_news_right']/h1/descendant::text()")
        title_.extend(page_.xpath("//div[@class='page_news_right']/h3/descendant::text()"))
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@class='page_news_right']/div[@class='news_artical']/p/descendant::text()")
        body_.extend(page_.xpath("//div[@class='page_news_right']/div[@class='news_artical']/div/descendant::text()"))
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
            
        return '\n'.join(data_)

    def __parse_almasryoon(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@id='news_shows']/div[@id='data_content_show2']/div[@id='head_topic']/div[@id='3nwan_cell']/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@id='news_shows']/p/descendant::text()")
        body_.extend(page_.xpath("//div[@id='news_shows']/div[@style='direction: rtl;']/descendant::text()"))
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
            
        return '\n'.join(data_)

    def __parse_alwafd(self, html_): # don't decode html from this website
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@class='article_title']/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@class='inside impress maincom']/p/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
            
        return '\n'.join(data_)
    
    def __parse_akhbar_elyom(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@id='ctl00_ContentPlaceHolder1_newsPlaceHolder']/table/tbody/tr[1]/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@id='ctl00_ContentPlaceHolder1_newsPlaceHolder']/table/tbody/tr/td[@class='articleBody']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
            
        ###################################################NEW FORMAT#####################################
        title_ = page_.xpath("//h4[@class='topicTitle']/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//p[@class='postTopicP']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
            
        return '\n'.join(data_)

    def __parse_elbadil(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//div[@id='content-region-inner']/h1/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//div[@class='field field-name-body field-type-text-with-summary field-label-hidden']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b: data_.append(b)
            
        return '\n'.join(data_)

    def __parse_dostor(self, html_):
        page_ = lxml.html.fromstring(html_)
        data_ = []
        title_ = page_.xpath("//table[@class='contentpaneopen']/descendant::*/td[@class='contentheading']/descendant::text()")
        for t in title_:
            t = t.encode('utf-8').strip()
            if t: data_.append(t)
            
        body_ = page_.xpath("//table[@class='contentpanebody']/descendant::*/div[@class='article_text']/descendant::text()")
        for b in body_:
            b = b.encode('utf-8').strip()
            if b and not 'pdf' in b and not u'تصفح جريدة الدستور اليوم'.encode('utf-8') in b: data_.append(b)
            
        return '\n'.join(data_)

    def __parse(self, news_site_, html_):
        if news_site_ == CONST.AKHBAR:
            return self.__parse_akhbarelyomgate(html_)
        elif news_site_ == CONST.SHOROUK:
            return self.__parse_shorouk(html_)
        elif news_site_ == CONST.CNN_ARABIC:
            return self.__parse_cnn_arabic(html_)
        elif news_site_ == CONST.ALMASRY_ELYOM:
            return self.__parse_almasryalyoum(html_)
        elif news_site_ == CONST.FAGR:
            return self.__parse_elfagr(html_)
        elif news_site_ == CONST.ENGLISH_AHRAM:
            return self.__parse_english_ahram(html_)
        elif news_site_ == CONST.FJP:
            return self.__parse_fjp(html_)
        elif news_site_ == CONST.MASRAWY:
            return self.__parse_masrawy(html_)
        elif news_site_ == CONST.AHRAM:
            return self.__parse_ahram_NEW_SITE(html_)
        elif news_site_ == CONST.BBC_ARABIC:
            return self.__parse_bbcarabic(html_)
        elif news_site_ == CONST.DOSTOR_ASLY:
            return self.__parse_dostorasly(html_)
        elif news_site_ == CONST.WATAN:
            return self.__parse_elwatannews(html_)
        elif news_site_ == CONST.ENGLISH_FJP:
            return self.__parse_english_fjp(html_)
        elif news_site_ == CONST.YOUM7:
            return self.__parse_youm7(html_)
        elif news_site_ == CONST.TAHRIR:
            return self.__parse_tahrir(html_)
        elif news_site_ == CONST.AKHBAR_MASR:
            return self.__parse_akhbar_masr(html_)
        elif news_site_ == CONST.RASD:
            return self.__parse_rasd(html_)
        elif news_site_ == CONST.MASRYOON:
            return self.__parse_almasryoon(html_)
        elif news_site_ == CONST.WAFD:
            return self.__parse_alwafd(html_)
        elif news_site_ == CONST.AKHBAR_ELYOM:
            return self.__parse_akhbar_elyom(html_)
        elif news_site_ == CONST.BADIL:
            return self.__parse_elbadil(html_)
        elif news_site_ == CONST.DOSTOR:
            return self.__parse_dostor(html_)
        else:
            print "Wrong News Site Name"

    def __parse_news_site(self, news_site_, json_index_):
        for path, v in json_index_.items():
            if v.has_key('parsed') and v['parsed'] == True: continue
            if news_site_ == CONST.YOUM7:
                text_ = self.__parse(news_site_, helper.READ_FILE(path).decode('windows-1256'))
            else:
                text_ = self.__parse(news_site_, helper.READ_FILE(path).decode('utf-8'))
            text_dir_ = os.path.dirname(path).replace('html', 'txt')
            if not os.path.exists(text_dir_): os.makedirs(text_dir_)
            file_ = "{0}.txt".format(os.path.basename(path)[:-5])
            text_file_ = os.path.join(text_dir_, file_)
            self._logger.log_info(text_file_)
            helper.WRITE_FILE(text_file_, text_)
            json_index_[path]['parsed'] = True
            helper.UPDATE_JSON_FILE(self._index_path, path, json_index_[path])

    # TODO: DELETE json_index_, will not use it anymore. DONE
    def __parse_news_site_db(self, news_site_):
        for index in self._db.select_unparsed_by_label(self._rss_label):
            path = index.file_path
            #assert path in json_index_.keys()
            #assert not json_index_[path].has_key('parsed') or not json_index_[path]['parsed']   
            if news_site_ == CONST.YOUM7:
                text_ = self.__parse(news_site_, helper.READ_FILE(path).decode('windows-1256'))
            else:
                text_ = self.__parse(news_site_, helper.READ_FILE(path).decode('utf-8'))
            text_dir_ = os.path.dirname(path).replace('html', 'txt')
            if not os.path.exists(text_dir_): os.makedirs(text_dir_)
            file_ = "{0}.txt".format(os.path.basename(path)[:-5])
            text_file_ = os.path.join(text_dir_, file_)
            self._logger.log_info(text_file_)
            helper.WRITE_FILE(text_file_, text_)
            #json_index_[path]['parsed'] = True
            self._db.set_parsed(path)
            #helper.UPDATE_JSON_FILE(self._index_path, path, json_index_[path])
    
    def __parse_news_from_mce(self, news_site_):
        for record in self._db.get_unparsed_html(news_site_):
            if news_site_ == CONST.WAFD:
                text_ = self.__parse(news_site_, helper.READ_FILE(record.news_html_filepath))
            elif news_site_ == CONST.YOUM7 or news_site_ == CONST.FAGR:
                text_ = self.__parse(news_site_, helper.READ_FILE(record.news_html_filepath).decode('windows-1256'))
            else:
                text_ = self.__parse(news_site_, helper.READ_FILE(record.news_html_filepath).decode('utf-8'))
                
            text_dir_ = os.path.dirname(record.news_html_filepath).replace('html', 'txt')
            with threading.Lock():
                if not os.path.exists(text_dir_): os.makedirs(text_dir_)
            file_ = "{0}.txt".format(os.path.basename(record.news_html_filepath)[:-5])
            text_file_ = os.path.join(text_dir_, file_)
            self._logger.log_info(text_file_)
            helper.WRITE_FILE(text_file_, text_)
            self._db.set_news_html_parsed(record.id)
                
    
    def parse_news_site(self):
        self._logger.log_info(self._rss_label)
        try:
            news_site_ = self._rss_label
            if '-' in news_site_:  news_site_ = news_site_.split('-')[0]
            
            if self._is_mce_news:
                self.__parse_news_from_mce(news_site_)
            else:
                self.__parse_news_site_db(news_site_)
        except:
            self._logger.log_error(self._rss_label, traceback.format_exc())

    def __init__(self, rss_label_, is_mce_news = False):
        self._logger = helper.Logger(CONST.HTML_PARSER_LOG_DIR)
        self._rss_label = rss_label_
        self._index_path = os.path.join(CONST.RSS_HTML_INDEX_DIR, "{0}.json".format(self._rss_label))
        self._db = db.IndexOperation() if not is_mce_news else db.MceWatchIndexOperation()
        self._is_mce_news = is_mce_news
        #if not os.path.exists(self._index_path):
        #    raise ValueError("Index: '{0}' doesn't exist.".format(self._index_path))
        

def PARSE(rss_labels_, is_mce_news = False):
    parsers_ = []
    for label in rss_labels_:
        try:
            parsers_.append(HTMLParser(label, is_mce_news))
        except:
            print traceback.format_exc()
    if not parsers_:
        print "Nothing to do."
        return
    #RUN_PARSER(parsers_[0])
    pool = Pool(processes=16)
    pool.map(RUN_PARSER, parsers_)
    pool.close()
    pool.join()
    print "Done"

def RUN_PARSER(parser_):
    parser_.parse_news_site()

if __name__ == '__main__':
    PARSE(CONST.RSS_LABELS)

def correct_index_format(rss_label_):
    try:
        index_path_ = os.path.join(CONST.RSS_HTML_INDEX_DIR, "{0}.json".format(rss_label_))
        index_ = helper.READ_JSON_FILE(index_path_)
        for k, v in index_.items():
            if type(v) == dict:
                continue
            index_[k] = {'url':v[0], 'data':v[1]}
        index_path_ = index_path_.replace('index', 'new_index')
        helper.WRITE_JSON_FILE(index_path_, index_)
    except:
        print rss_label_, '\n\n', traceback.format_exc()

def correct_index(rss_label_):
    try:
        index_path_ = os.path.join(CONST.RSS_HTML_INDEX_DIR, "{0}.json".format(rss_label_))
        index_ = helper.READ_JSON_FILE(index_path_)
        for k, v in index_.items():
            v['date'] = v['data']
            del v['data']
            index_[k] = v
        index_path_ = index_path_.replace('index', 'new_index')
        helper.WRITE_JSON_FILE(index_path_, index_)
    except:
        print rss_label_, '\n', traceback.format_exc()
