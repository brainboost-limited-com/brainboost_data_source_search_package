from src.YahooSearchEngine import YahooSearchEngine



class AolSearchEngine(YahooSearchEngine):
    '''Seaches aol.com'''
    def __init__(self, proxy=None, timeout=10):
        super(AolSearchEngine, self).__init__(proxy, timeout)
        self._base_url = u'https://search.aol.com'

    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/aol/search?q={}&ei=UTF-8&nojs=1'
        url = url_str.format(self._base_url, self._query)
        self._http_client.get(self._base_url)
        return {'url':url, 'data':None}

