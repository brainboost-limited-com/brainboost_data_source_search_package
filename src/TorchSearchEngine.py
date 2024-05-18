from src.SearchEngine import SearchEngine



class TorchSearchEngine(SearchEngine):
    '''Uses torch search engine. Requires TOR proxy.'''
    def __init__(self, proxy=None, timeout=10):
        super(TorchSearchEngine, self).__init__(proxy, timeout)
        self._base_url = u'http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion'
        if not proxy:
            print('Torch requires TOR proxy!')
        self._current_page = 1
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'h5 a[href]', 
            'title': 'h5 a[href]', 
            'text': 'p', 
            'links': 'div.result.mb-3', 
            'next': 'ul.pagination a.page-link'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/search?query={}&action=search'
        url = url_str.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        self._current_page += 1
        url_str = u'{}/search?query={}&page={}'
        url = url_str.format(self._base_url, self._query, self._current_page)
        return {'url':url, 'data':None}
