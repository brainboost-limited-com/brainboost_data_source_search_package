from src.SearchEngine import SearchEngine
from brainboost_data_source_requests_package.UserAgentPool import UserAgentPool

class BingSearchEngine(SearchEngine):
    '''Searches bing.com'''
    def __init__(self, proxy=None, timeout=10):
        super(BingSearchEngine, self).__init__(proxy, timeout)
        self._base_url = u'https://www.bing.com'
        uap = UserAgentPool()
        self.set_headers({'User-Agent':uap.get_random_user_agent()})

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.b_attribution cite', 
            'title': 'h2', 
            'text': 'p', 
            'links': 'ol#b_results > li.b_algo', 
            'next': 'div#b_content nav[role="navigation"] a.sb_pagN'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        self._get_page(self._base_url)
        url = u'{}/search?q={}&search=&form=QBLH'.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = (self._base_url + next_page) 
        return {'url':url, 'data':None}

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results items.'''
        return super(BingSearchEngine, self)._get_url(tag, 'text')
