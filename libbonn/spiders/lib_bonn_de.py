from enum import Enum
from queue import Queue
from requests import Response
from urllib.parse import urlencode

import logging
import re
import scrapy


class LibBonnDeSpider(scrapy.Spider):
    name = 'lib.bonn.de'
    allowed_domains = ['lib.bonn.de']
    start_urls = [
        'https://lib.bonn.de/webOPACClient/start.do?Lang=de&Login=web00&BaseURL=this']

    categories = [
        '-1',
        '100',
        '331',
        '902',
        '14',
        '700',
        '412',
        '540',
        '451',
        '425',
        '712',
    ]

    view_locations = [
        '0',
        '2',
        '6',
        '9',
        '10',
        '11',
        '12',
        '13',
        '17',
    ]

    locations = [
        '',
        '0',
        '1',
        '2',
        '6',
        '7',
        '9',
        '10',
        '11',
        '12',
        '13',
        '14',
        '17',
        '20',
        '21',
    ]

    languages = [
        '',
        '33',
        '29',
        '23',
        '24',
        '25',
        '26',
        '27',
        '34',
        '28',
        '30',
        '35',
    ]

    medias = [
        '',
        '22',
        '19',
        '12',
        '36',
        '20',
        '31',
        '11',
        '15',
        '21',
        '32',
        '37',
    ]

    operators = {
        '&': 'AND',
        '|': 'OR',
        '^': 'NOT'
    }

    sort_options = {
        'location': '1',
        'status': '2'
    }

    # default config
    search_category = categories[0]
    search = ''

    search2_operator = operators['&']
    search2_category = categories[0]
    search2 = ''

    search3_operator = operators['&']
    search3_category = categories[0]
    search3 = ''

    view_location = view_locations[0]
    location = locations[0]

    language = languages[0]
    media = medias[0]

    year_start = ''
    year_end = ''

    sort = sort_options['location']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        if 'search' in kwargs:
            m_search = re.search(
                '^(?:(?P<category>\d*):)?(?P<search>.*$)', kwargs['search'])
            if m_search:
                dict = m_search.groupdict()
                if dict['category']:
                    if not dict['category'] in self.categories:
                        logging.warning(
                            'Using unsupported search category \'%s\' for search' % dict['category'])
                    self.search_category = dict['category']
                if dict['search']:
                    self.search = dict['search']

        if 'search2' in kwargs:
            m_search = re.search(
                '(?:(?P<operator>[&|^]?)(?P<category>\d*):)?(?P<search>.*)', kwargs['search2'])
            if m_search:
                dict = m_search.groupdict()
                if dict['operator']:
                    if not dict['operator'] in self.operators:
                        logging.warning(
                            'Using unsupported search operator \'%s\' for search2' % dict['operator'])
                    self.search2_operator = dict['operator']
                if dict['category']:
                    if not dict['category'] in self.categories:
                        logging.warning(
                            'Using unsupported search category \'%s\' for search2' % dict['category'])
                    self.search2_category = dict['category']
                if dict['search']:
                    self.search2 = dict['search']

        if 'search3' in kwargs:
            m_search = re.search(
                '(?:(?P<operator>[&|^]?)(?P<category>\d*):)?(?P<search>.*)', kwargs['search3'])
            if m_search:
                dict = m_search.groupdict()
                if dict['operator']:
                    if not dict['operator'] in self.operators:
                        logging.warning(
                            'Using unsupported search operator \'%s\' for search3' % dict['operator'])
                    self.search3_operator = dict['operator']
                if dict['category']:
                    if not dict['category'] in self.categories:
                        logging.warning(
                            'Using unsupported search category \'%s\' for search3' % dict['category'])
                    self.search3_category = dict['category']
                if dict['search']:
                    self.search3 = dict['search']

        if 'view_location' in kwargs:
            if not kwargs['view_location'] in self.view_locations:
                logging.warning(
                    'Using unsupported view_location \'%s\'' % kwargs['view_location'])
            self.view_location = kwargs['view_location']

        if 'location' in kwargs:
            if not kwargs['location'] in self.locations:
                logging.warning('Using unsupported location \'%s\'' %
                                kwargs['location'])
            self.location = kwargs['location']

        if 'language' in kwargs:
            if not kwargs['language'] in self.locations:
                logging.warning('Using unsupported language \'%s\'' %
                                kwargs['language'])
            self.language = kwargs['language']

        if 'media' in kwargs:
            if not kwargs['media'] in self.media:
                logging.warning('Using unsupported media \'%s\'' %
                                kwargs['media'])
            self.media = kwargs['media']

        if 'year' in kwargs:
            m_search = re.search(
                '(?P<year_start>\d{4})(?:[:](?P<year_end>\d{4}))', kwargs['year'])
            if m_search:
                dict = m_search.groupdict()
                if dict['year_start']:
                    self.year_start = dict['year_start']

                if dict['year_end']:
                    self.year_end = dict['year_end']
            else:
                logging.error('Illegal argument value for year: %s' %
                              kwargs['year'])

    def parse(self, response):
        csid = response.selector.xpath(
            '//*[@id="AdvancedSearchForm"]/input[2]/@value').get()

        query_data = {
            'methodToCall': 'switchSearchPage',
            'SearchType': '2'
        }

        yield scrapy.Request(url=response.urljoin('search.do?' + urlencode(query_data)),
                             callback=self.prepare_search_parameters,
                             dont_filter=True)

    def prepare_search_parameters(self, response):
        csid = response.selector.xpath(
            '//*[@id="AdvancedSearchForm"]/input[2]/@value').get()

        query_data = {'methodToCall': 'submit',
                      'CSId': csid,
                      'methodToCallParameter': 'searchPreferences',
                      'callingPage': 'searchParameters',
                      'selectedViewBranchlib': self.view_location,
                      'selectedSearchBranchlib': self.location,
                      'searchRestrictionID[0]': '7',  # hidden
                      'searchRestrictionValue1[0]': self.language,
                      'searchRestrictionID[1]': '6',  # hidden
                      'searchRestrictionValue1[1]': self.media,
                      'searchRestrictionID[2]': '1',  # hidden
                      # von Ersch.-Jahr
                      'searchRestrictionValue1[2]': self.year_start,
                      # bis Ersch.-Jahr
                      'searchRestrictionValue2[2]': self.year_end,
                      }

        yield scrapy.Request(url=response.urljoin('search.do?' + urlencode(query_data)),
                             callback=self.prepare_search_preferences,
                             dont_filter=True)

    def prepare_search_preferences(self, response):
        csid = response.selector.xpath(
            '//*[@id="AdvancedSearchForm"]/input[2]/@value').get()

        query_data = {'methodToCall': 'submit',
                      'CSId': csid,
                      'methodToCallParameter': 'submitSearch',
                      'searchCategories[0]': self.search_category,
                      'searchString[0]': self.search,
                      'combinationOperator[1]': self.search2_operator,
                      'searchCategories[1]': self.search2_category,
                      'searchString[1]': self.search2,
                      'combinationOperator[2]': self.search3_operator,
                      'searchCategories[2]': self.search3_category,
                      'searchString[2]': self.search3,
                      'submitSearch': 'Suchen',
                      'callingPage': 'searchPreferences',
                      'exemplarSorting': self.sort,
                      'numberOfHits': '100',  # We might crawl a lot of pages so always use biggest value
                      'rememberList': '-1',  # Temporäre Merkliste, single option here
                      'timeOut': '120',  # max timeout
                      'considerSearchRestriction': '2',  # hidden
                      }

        yield scrapy.Request(url=response.urljoin('search.do?' + urlencode(query_data)),
                             callback=self.parse_hitlist,
                             dont_filter=True)

    def parse_hitlist(self, response: Response):
        selector = response.selector

        next_page_url = selector.xpath(
            '//*[@id="hitlist"]/div/div[1]/div/div/*[@aria-label=\'Nächste Seite\']/@href').get()
        next_page = response.urljoin(next_page_url) if next_page_url else None

        hit_urls = Queue()
        for hit in selector.xpath('//*[@id="hitlist"]/div/table/tr'):
            hit_media_type = hit.xpath('.//td[1]/img/@title').get().strip()
            hit_url = hit.xpath('.//td[2]/a[2]/@href').get()
            if hit_url:
                hit_urls.put({'url': response.urljoin(hit_url), 'media_type': hit_media_type})

        if not hit_urls.empty():
            next_hit = hit_urls.get()
            yield scrapy.Request(url=next_hit['url'],
                                 meta={'next_hits': hit_urls,
                                       'next_page': next_page,
                                       'media_type': next_hit['media_type']},
                                 callback=self.parse_hit,
                                 dont_filter=True)

    def parse_hit(self, response: Response):
        selector = response.selector

        i = 1
        columns = []
        while True:
            column = selector.xpath(
                '//*[@id="tab-content"]/table/tr[@id="bg2"]/th[%i]/text()' % i).get()
            if column:
                column = column.strip()
            if not column:
                column = selector.xpath(
                    '//*[@id="tab-content"]/table/tr[@id="bg2"]/th[%i]/p/text()' % i).get()
            if column:
                column = column.strip()
            if not column:
                break

            columns.append(column)
            i = i+1

        items = []
        for row in selector.xpath('//*[@id="tab-content"]/table/tr[not(@id="bg2")]'):
            item = {}
            for i, column in enumerate(columns):
                value = row.xpath('.//td[%s]/text()' % (i + 1)).get()
                if value:
                    value = value.strip()
                if value:
                    item[column] = value
            if item:
                items.append(item)

        yield scrapy.Request(url=response.urljoin(selector.xpath('//*[@id="labelTitle"]/a/@href').get()),
                             meta={
                                 'next_hits': response.meta['next_hits'], 'next_page': response.meta['next_page'], 'items': item, 'media_type': response.meta['media_type'] },
                             callback=self.parse_hit_tab,
                             dont_filter=True)

    def parse_hit_tab(self, response):
        selector = response.selector

        content = selector.xpath('//*[@id="tab-content"]/table/tr/td')

        i = 1
        attributes = {}
        if response.meta['media_type']:
            attributes['Medientyp'] = response.meta['media_type']
        while True:
            key = content.xpath('.//strong[%s]/text()' % i).get()
            if not key:
                break

            value = content.xpath('.//div[%s]/text()' % i).get()
            i = i+1
            if not value:
                continue

            sanitized_key = key.strip().strip(':')
            sanitized_value = value.strip()

            if sanitized_key in attributes:
                if isinstance(attributes[sanitized_key], list):
                    if not sanitized_value in attributes[sanitized_key]:
                        attributes[sanitized_key].append(sanitized_value)
                elif attributes[sanitized_key] != sanitized_value:
                    attributes[sanitized_key] = [
                        attributes[sanitized_key], sanitized_value]
            else:
                attributes[sanitized_key] = [sanitized_value]

        attributes['Exemplare'] = response.meta['items']

        yield attributes

        if not response.meta['next_hits'].empty():
            next_hit = response.meta['next_hits'].get()
            yield scrapy.Request(url=next_hit['url'],
                                 meta={
                                     'next_hits': response.meta['next_hits'], 
                                     'next_page': response.meta['next_page'], 
                                     'media_type': next_hit['media_type']},
                                 callback=self.parse_hit,
                                 dont_filter=True)
        elif response.meta['next_page']:
            yield scrapy.Request(url=response.meta['next_page'],
                                 callback=self.parse_hitlist,
                                 dont_filter=True)
