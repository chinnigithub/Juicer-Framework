from juicer.items import *
from juicer.utils import *
from pprint import pprint
import urllib2

class WikiKurdishBrowse(JuicerSpider):
    name = 'wiki_kurdish_browse'
    start_urls = ['https://en.wikipedia.org/wiki/List_of_Kurdish-language_television_channels']

    def __init__(self, *args, **kwargs):
        super(WikiKurdishBrowse, self).__init__(*args, **kwargs)
        self.info_query = 'insert into wiki_infobox (gid, title, aka, affiliations, former_affiliations,                            former_callsigns, owned_by, launched, format, country, broadcast_area, slogan,                            sister_channels, website, logo, aux_info, created_at, modified_at)                            values(%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,                            now(), now()) on duplicate key update modified_at=now(), title=%s ,                           gid = %s, aux_info=%s, format=%s, owned_by=%s, launched=%s, slogan=%s,                           affiliations=%s,former_affiliations=%s,former_callsigns=%s, website=%s,                           country=%s, broadcast_area=%s, aka=%s'
        self.channel_query = 'insert into wiki_channels(gid, callsign, title, type, original_title, network,                              section, region, category, reference_url, aux_info, created_at, modified_at)                              values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())                              on duplicate key update modified_at=now(), region = %s, aux_info = %s,                              category = %s, reference_url = %s, section = %s, original_title=%s,                              network = %s, type=%s'
        self.no_info_query = 'insert into wiki_nopages (gid, title, created_at, modified_at)                              values(%s, %s, now(),now()) on duplicate key update modified_at=now()'
        self.conn = MySQLdb.connect(host='localhost', db='WIKIDB_CHANNELS', user='root', passwd='', charset='utf8', use_unicode=True)
        self.conn.autocommit(True)
        self.cur = self.conn.cursor()
        self.gid_patt = re.compile('"wgArticleId":(\\d+)')
        self.french_months = {u'janvier': '01',
         u'f\xe9vrier': '02',
         u'mars': '03',
         u'avril': '04',
         u'mai': '05',
         u'juin': '06',
         u'juillet': '07',
         u'ao\xfbt': '08',
         u'septembre': '09',
         u'octobre': '10',
         u'novembre': '11',
         u'd\xe9cembre': '12'}



    def __del__(self):
        self.conn.close()
        self.cur.close()



    def parse(self, response):
        sel = Selector(response)
        category = 'Turkish Kurdistan (Bakur)'
        if category == 'Turkish Kurdistan (Bakur)':
            chann_aux = {}
            channel = sel.xpath('//span[contains(text(), "Turkish Kurdistan (Bakur)")]/../following-sibling::ul[1]/li/a/text()').extract()[-1]
            ori_tit = ''.join(sel.xpath('//span[contains(text(), "Turkish Kurdistan (Bakur)")]/../following-sibling::ul[1]/li/a/@title').extract())
            channel_href = sel.xpath('//span[contains(text(), "Turkish Kurdistan (Bakur)")]/../following-sibling::ul[1]/li/a/@href').extract()[-1]
            channel_text = ''.join(sel.xpath('//span[contains(text(), "Turkish Kurdistan (Bakur)")]/../following-sibling::ul[1]/li/a/../text()').extract()).replace(u'\u2013', '').strip().strip('-')
            channel_text = re.sub(channel, '', channel_text)
            if channel:
                if channel_text:
                    chann_aux.update({'channel_info': channel_text})
                chann_aux.update({'ref_url': response.url})
                self.insert_data_into_db(channel, ori_tit, channel_href, chann_aux, category, response.url, '')
            sub_cat_node = sel.xpath('//span[contains(text(), "Defunct")]/../following-sibling::ul[1]/li')
            for i in sub_cat_node:
                chann_aux = {}
                channel = extract_data(i, './a[1]/text()')
                ori_tit = extract_data(i, './a[1]/@title')
                chann_txt = ''.join(i.xpath('.//text()').extract()).replace(u'\u2013', '').strip().strip('-')
                channel_href = extract_data(i, './a[1]/@href')
                chann_txt = re.sub(channel, '', chann_txt)
                if channel:
                    if chann_txt:
                        chann_aux.update({'channel_info': chann_txt})
                    chann_aux.update({'ref_url': response.url})
                    self.insert_data_into_db(channel, ori_tit, channel_href, chann_aux, category, response.url, 'Defunct')

        categories = sel.xpath('//div[@id="mw-content-text"]/h2/span/text()').extract()
        for category in categories:
            cat_nodes = sel.xpath('//span[contains(text(), "%s")]/../following-sibling::ul[1]/li' % category)
            for cat in cat_nodes:
                (chann_aux, ori_tit,) = ({}, '')
                inn_nodes = cat.xpath('./ul/li')
                channel = extract_data(cat, './a[1]/text()')
                ori_tit = extract_data(cat, './a[1]/@title')
                channel_href = extract_data(cat, './a[1][not(contains(., "United States"))][not(contains(text(), "Canada"))]/@href')
                channel_text = '<>'.join(cat.xpath('./text()').extract()).replace(u'\u2013', '').strip().strip('-')
                if '<>,' in channel_text or channel_text == '(<>)':
                    channel_text = extract_data(cat, './/text()', '<>')
                channel_temp = channel_text.strip('()').replace(', ', '<>').replace('<>(', '<>').replace(' (', '<>').replace('<><>', '<>').replace(',<>', '<>').replace('<><>', '<>').strip('<>').replace('and<>', '<>')
                if channel_temp:
                    chann_aux.update({'channel_info': re.sub(channel, '', channel_temp).strip('<>').replace(' and ', '<>'),
                     'ref_url': response.url})
                if not channel or 'United' in channel:
                    channel = channel_text
                    ori_tit = channel
                if '<>' in channel:
                    channel = channel.split('<>')[0]
                if '(' in channel:
                    channel = channel.split('(')[0].strip()
                    ori_tit = channel
                if inn_nodes:
                    for inn_node in inn_nodes:
                        channel_href = extract_data(inn_node, './a/@href')
                        channel = extract_data(inn_node, './a/text()')
                        chann_txt = ''.join(inn_node.xpath('.//text()').extract()).replace(u'\u2013', '').strip().strip('-')
                        if chann_txt:
                            chann_aux.update({'channel_info': re.sub(channel, '', chann_txt).strip('<>'),
                             'ref_url': response.url})
                        self.insert_data_into_db(channel, ori_tit, channel_href, chann_aux, category, response.url, '')

                self.insert_data_into_db(channel, ori_tit, channel_href, chann_aux, category, response.url, '')





    def insert_data_into_db(self, channel, ori_tit, channel_href, chann_aux, category, ref_url, section):
        (channel_gid, chann_ref,) = ('', '')
        (flag, channel_dict,) = (False, {})
        if channel_href:
            channel_href = self.wiki_url_format(channel_href)
            channel_dict = self.get_wiki_details(channel_href)
            channel_gid = channel_dict.get('wikigid', '')
            flag = True
            chann_ref = channel_href
        if channel and channel_gid == '':
            channel_gid = self.get_gid(channel)[0]
            flag = False
            chann_ref = ref_url
        if 'Note:' in channel:
            channel = ''
        (logo, website, slogan, sisters_channel, broadcast_area, format_, owned_by,) = [''] * 7
        wikigid = channel_dict.get('wikigid', '')
        infoboxes = channel_dict.get('infoboxes', {})
        launched = channel_dict.get('launched', '')
        aka = channel_dict.get('aka', '').replace(',', '<>').replace('<> ', '<>')
        sisters = channel_dict.get('sisters', '')
        wikititle = channel_dict.get('wikititle', '')
        country = channel_dict.get('country', '').replace('<>(soon)', '')
        affiliates = self.remove_url(self.replace_with_brackets(channel_dict.get('affiliates', '')))
        former_callsigns = self.remove_url(self.replace_with_brackets(channel_dict.get('f_callsigns', '')))
        former_affiliations = self.remove_url(self.replace_with_brackets(channel_dict.get('f_affiliates', '')))
        website = self.remove_url(channel_dict.get('website', '')).replace('<>.', '.').replace('[1]#<#', '')
        if infoboxes:
            logo = infoboxes.get('logo', '').replace('logo#<#', '')
            if not logo:
                logo = infoboxes.get('logo_info', '')
                if '#<#' in logo:
                    logo = logo.split('#<#')[-1]
            owned_by = self.replace_with_brackets(self.remove_url(infoboxes.get('Owned by', '')))
            if not owned_by:
                owned_by = self.replace_with_brackets(self.remove_url(infoboxes.get('Owner', '')))
            if not owned_by:
                owned_by = self.replace_with_brackets(self.remove_url(infoboxes.get('Propri\xc3\xa9taire', '')))
            format_ = self.replace_with_brackets(self.remove_url(self.replace_with_brackets(infoboxes.get('Picture format', '')))).replace('(<>', '(').replace('<>[1]', '')
            if not format_:
                format_ = self.replace_with_brackets(self.remove_url(self.replace_with_brackets(infoboxes.get('Format', '')))).replace('(<>', '(').replace('<>[1]', '')
            if not format_:
                format_ = self.replace_with_brackets(self.remove_url(self.replace_with_brackets(infoboxes.get("Format d'image", '')))).replace('(<>', '(').replace('<>[1]', '')
            website = infoboxes.get('Website', '').replace('<>.', '.')
            if not website:
                website = self.remove_url(infoboxes.get('Official website', '')).replace('<>.', '.')
            slogan = infoboxes.get('Slogan', '').replace(', ', '<>').replace('<>(', ' (')
            if not country:
                country = self.remove_url(infoboxes.get('Country', '')).replace('<>(soon)', '')
            if not country:
                country = self.remove_url(infoboxes.get('Pays', '')).replace('<>(soon)', '')
            if len(country) > 50:
                country = ''
            sisters_channel = self.replace_with_brackets(self.remove_url(infoboxes.get('Sister channel(s)', ''))).replace(' & ', '')
            broadcast_area = infoboxes.get('Broadcast area', '').replace(' , ', '<>').replace(';', '<>').replace('<> ', '<>')
            if '#<#https' in broadcast_area:
                broadcast_area = broadcast_area.split('#<#https')[0].replace(',', '<>').replace(' <> ', '<>')
            if not former_affiliations:
                former_affiliations = self.remove_url(self.replace_with_brackets(infoboxes.get('Formeraffiliations', '')))
            if not former_affiliations:
                former_affiliations = self.remove_url(self.replace_with_brackets(infoboxes.get('Former affiliations', '')))
            if not affiliates:
                affiliates = self.remove_url(self.replace_with_brackets(infoboxes.get('Affiliates', '')))
            if not affiliates:
                affiliates = self.remove_url(self.replace_with_brackets(infoboxes.get('Affili\xc3\xa9s', '')))
            if not launched:
                launched = infoboxes.get('Launched', '')
            if not launched:
                launched = infoboxes.get('Launch date', '')
            if not launched:
                launched = infoboxes.get('Lancement', '')
            if launched:
                launched = re.findall('(\\d{4})-(\\d+)-(\\d+)', launched)
                if launched:
                    launched = '-'.join(launched[0])
                else:
                    launched = ''
            if not launched:
                launched_ = infoboxes.get('Launch date', '')
                if not launched_:
                    launched_ = infoboxes.get('Launched', '')
                if launched_:
                    lan = re.findall('(\\d+) (\\D+), (\\d{4})', launched_)
                    if lan:
                        (day, month, year,) = lan[0]
                        date = day + '-' + month + '-' + year
                    else:
                        date = ''
                    if not lan:
                        lan = re.findall('(\\D+) (\\d+), (\\d{4})', launched_)
                        if lan:
                            (month, day, year,) = lan[0]
                            date = day + '-' + month.replace(')<>', '') + '-' + year
                    if date:
                        date_ = datetime.datetime.strptime(date, '%d-%B-%Y')
                        launched = str(date_.date())
            if not launched:
                laun = infoboxes.get('Lancement', '')
                if laun:
                    laun = re.findall('(\\d+)<>(\\D+)<>(\\d{4})', laun)
                    if laun:
                        (day, month, year,) = laun[0]
                        m_no = self.french_months.get(month.strip(), '')
                        if m_no:
                            launched = '%s-%s-%s' % (year, m_no, day)
        ori_tit = ori_tit.replace('(page does not exist)', '').strip()
        if website and '#<#' in website:
            website = website.split('#<#')[-1]
        if website and 'http' not in website:
            website = 'http://' + website
        category = self.replace_with_brackets(category)
        affiliates = affiliates.replace('Lists:', '').strip('<>')
        channel = channel.replace('[8]', '').replace('[9]', '').replace('[10]', '')
        channel = re.sub('\\((.*?)\\)', '', channel).strip()
        ori_tit = ori_tit.strip('<>').replace('(<>and<>)', '')
        owned_by = owned_by.replace('<><>', '<>').replace('(<>', '(').strip('<>').replace('<>(', ' (')
        aka = aka.replace('<>(', ' (')
        broadcast_area = broadcast_area.replace(', ', '<>').replace('<>(', ' (')
        country = country.replace(', ', '<>').replace('and<>', '<>')
        format_ = format_.replace(' et<>', '<>')
        type_ = chann_aux.get('type', '')
        channel = self.name_clean(channel)
        ori_tit = self.name_clean(ori_tit)
        if '(' in ori_tit:
            ori_tit = ori_tit.split('(')[0].strip()
        if channel_gid and channel:
            if chann_aux:
                ch_aux = json.dumps(chann_aux, ensure_ascii=False, encoding='utf-8')
            else:
                ch_aux = ''
            chann_values = (channel_gid,
             channel.replace(' ', ''),
             channel,
             type_,
             ori_tit,
             '',
             section,
             'KUR',
             category,
             chann_ref,
             ch_aux,
             'KUR',
             ch_aux,
             category,
             chann_ref,
             section,
             ori_tit,
             '',
             type_)
            print category,
            print '***',
            print channel
            self.cur.execute(self.channel_query, chann_values)
            self.conn.commit()
            if flag and channel:
                if infoboxes:
                    aux = json.dumps(infoboxes)
                else:
                    aux = ''
                info_values = (channel_gid,
                 channel,
                 aka,
                 affiliates,
                 former_affiliations,
                 former_callsigns,
                 owned_by,
                 launched,
                 format_,
                 country,
                 broadcast_area,
                 slogan,
                 sisters_channel,
                 website,
                 logo,
                 aux,
                 channel,
                 channel_gid,
                 aux,
                 format_,
                 owned_by,
                 launched,
                 slogan,
                 affiliates,
                 former_affiliations,
                 former_callsigns,
                 website,
                 country,
                 broadcast_area,
                 aka)
                self.cur.execute(self.info_query, info_values)
                self.conn.commit()
            elif channel:
                no_infi_values = (channel_gid, channel)
                self.cur.execute(self.no_info_query, no_infi_values)
                self.conn.commit()



    def get_wikiarticle_id(self, href):
        (status, sel,) = get_response(href, self.log)
        if status == 200:
            pro_data_txt = extract_data(sel, '//script')
            if pro_data_txt:
                progid = textify(self.gid_patt.findall(pro_data_txt))
                win_pro = 'WIKI' + progid
                return win_pro
            else:
                return ''
        else:
            return ''



    def replace_with_brackets(self, text):
        lst = [',',
         '/',
         '<>[1]<>',
         '<>/<>',
         ' and ',
         '<> ',
         ' <>',
         '<><><>',
         '<><>',
         '<>,',
         '<>&<>']
        for i in lst:
            text = text.replace(i, '<>')

        return text.strip('<>').replace('<>[2]', '').replace('<>[3]', '').replace('<>[4]', '')



    def remove_url(self, text):
        if text and '#<#' in text:
            text = text.split('#<#')[0]
        return text

