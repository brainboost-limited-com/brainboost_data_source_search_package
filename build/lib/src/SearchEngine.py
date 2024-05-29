from bs4 import BeautifulSoup
from time import sleep
from random import uniform as random_uniform
import requests
import sys
from src.SearchResults import SearchResults
from brainboost_data_source_requests_package.TorRequest import TorRequest
import src.output as out
import src.config as cfg


class SearchEngine(object):
    '''The base class for all Search Engines.'''

    def __init__(self, proxy=None, timeout=10):
        '''
        :param str proxy: optional, a proxy server  
        :param int timeout: optional, the HTTP timeout
        '''
        self._http_client = TorRequest() 
        self._delay = (1, 4)
        self._query = ''
        self._filters = []

        self.results = SearchResults()
        '''The search results.'''
        self.ignore_duplicate_urls = False
        '''Collects only unique URLs.'''
        self.ignore_duplicate_domains = False
        '''Collects only unique domains.'''
        self.is_banned = False
        '''Indicates if a ban occurred'''

    def quote_url(self, url, safe=';/?:@&=+$,#'):
        '''Encodes URLs.'''
        if sys.version_info[0] < 3:
            url = self.encode_str(url)
        return requests.utils.quote(url, safe=safe)

    def unquote_url(self, url):
        '''Decodes URLs.'''
        if sys.version_info[0] < 3:
            url = self.encode_str(url)
        return self.decode_bytes(requests.utils.unquote(url))

    def is_url(self, link):
        '''Checks if link is URL'''
        parts = requests.utils.urlparse(link)
        return bool(parts.scheme and parts.netloc)

    def domain(self, url):
        '''Returns domain from URL'''
        host = requests.utils.urlparse(url).netloc
        return host.lower().split(':')[0].replace('www.', '')

    def encode_str(self, s, encoding='utf-8', errors='replace'):
        '''Encodes unicode to str, str to bytes.'''
        return s if type(s) is bytes else s.encode(encoding, errors=errors)

    def decode_bytes(self, s, encoding='utf-8', errors='replace'):
        '''Decodes bytes to str, str to unicode.'''
        return s.decode(encoding, errors=errors) if type(s) is bytes else s

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'links': 'a.search-result',  # Example selector
            'title': 'h2.title',         # Example selector
            'text': 'p.preview'          # Example selector
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page URL.'''
        # Implement according to the specific search engine's first page URL logic
        return {'url': 'https://www.example.com/search?q=' + self._query, 'data': None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data.'''
        # Implement pagination logic based on search engine structure
        next_button = tags.select_one('a.next')
        if next_button:
            return {'url': self.unquote_url(next_button['href']), 'data': None}
        return {'url': None, 'data': None}
    
    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results items.'''
        return self.unquote_url(tag.get(item, ''))

    def _get_title(self, tag, item='text'):
        '''Returns the title of search results items.'''
        return tag.get_text().strip()

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        return tag.get_text().strip()

    def _get_page(self, page, data=None):
        '''Gets pagination links.'''
        if data:
            return self._http_client.post(page, data)
        return self._http_client.get(page)

    def _get_tag_item(self, tag, item):
        '''Returns Tag attributes.'''
        if not tag:
            return u''
        return tag.text if item == 'text' else tag.get(item, u'')

    def _item(self, link):
        '''Returns a dictionary of the link data.'''
        return {
            'host': self.domain(self._get_url(link)), 
            'link': self._get_url(link), 
            'title': self._get_title(link).strip(), 
            'text': self._get_text(link).strip()
        } 

    def _query_in(self, item):
        '''Checks if query is contained in the item.'''
        return self._query.lower() in item.lower()
    
    def _filter_results(self, soup):
        '''Processes and filters the search results.''' 
        tags = soup.select(self._selectors('links'))
        results = [self._item(tag) for tag in tags]

        if u'url' in self._filters:
            results = [item for item in results if self._query_in(item['link'])]
        if u'title' in self._filters:
            results = [item for item in results if self._query_in(item['title'])]
        if u'text' in self._filters:
            results = [item for item in results if self._query_in(item['text'])]
        if u'host' in self._filters:
            results = [item for item in results if self._query_in(self.domain(item['link']))]
        return results
    
    def _collect_results(self, items):
        '''Collects the search results items.''' 
        for item in items:
            if not self.is_url(item['link']):
                continue
            if item in self.results:
                continue
            if self.ignore_duplicate_urls and item['link'] in self.results.links():
                continue
            if self.ignore_duplicate_domains and item['host'] in self.results.hosts():
                continue
            self.results.append(item)

    def _is_ok(self, response):
        '''Checks if the HTTP response is 200 OK.'''
        self.is_banned = response.status_code in [403, 429, 503]
        
        if response.status_code == 200:
            return True
        msg = ('HTTP ' + str(response.status_code)) if response.status_code else response.text
        print(msg)
        return False
    
    def disable_console(self):
        '''Disables console output'''
        out.console = lambda msg, end='\n', level=None: None
    
    def set_headers(self, headers):
        '''Sets HTTP headers.
        
        :param headers: dict The headers 
        '''
        self._http_client.session.headers.update(headers)
    
    def set_search_operator(self, operator):
        '''Filters search results based on the operator. 
        Supported operators: 'url', 'title', 'text', 'host'

        :param operator: str The search operator(s)
        '''
        operators = self.decode_bytes(operator or u'').lower().split(u',')
        supported_operators = [u'url', u'title', u'text', u'host']

        for operator in operators:
            if operator not in supported_operators:
                msg = u'Ignoring unsupported operator "{}"'.format(operator)
                print(msg)
            else:
                self._filters += [operator]
    
    def search(self, query, pages=1): 
        '''Perform a search and collect results.'''
        print('Searching {}'.format(self.__class__.__name__))
        self._query = self.decode_bytes(query)
        self.results = SearchResults()
        request = self._first_page()

        for page in range(1, pages + 1):
            try:
                response = self._get_page(request['url'], request['data'])
                if not self._is_ok(response):
                    break
                tags = BeautifulSoup(response.text, "html.parser")
                items = self._filter_results(tags)
                self._collect_results(items)
                
                msg = 'page: {:<8} links: {}'.format(page, len(self.results))
                print(msg, end='')
                request = self._next_page(tags)

                if not request['url']:
                    break
                if page < pages:
                    sleep(random_uniform(*self._delay))
            except KeyboardInterrupt:
                break
        print('', end='')
        return self.results
    

    def search_with_preview(self, query, pages=1):
        '''Search and print results including preview text.'''
        print('Searching {}'.format(self.__class__.__name__))
        self._query = self.decode_bytes(query)
        self.results = SearchResults()
        request = self._first_page()

        for page in range(1, pages + 1):
            try:
                response = self._get_page(request['url'], request['data'])
                if not self._is_ok(response):
                    break
                tags = BeautifulSoup(response.text, "html.parser")
                items = self._filter_results(tags)
                self._collect_results(items)
                
                msg = 'page: {:<8} links: {}'.format(page, len(self.results))
                print(msg, end='')
                request = self._next_page(tags)

                if not request['url']:
                    break
                if page < pages:
                    sleep(random_uniform(*self._delay))
            except KeyboardInterrupt:
                break
        print('', end='')
        return self.results
