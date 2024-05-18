from src.SearchEngine import SearchEngine
from brainboost_data_source_requests_package.UserAgentPool import UserAgentPool

class MojeekSearchEngine(SearchEngine):
    '''Searches mojeek.com'''
    def __init__(self, proxy=None, timeout=10):
        super(MojeekSearchEngine, self).__init__(proxy, timeout)
        self._base_url = 'https://www.mojeek.com'
        ua = UserAgentPool()
        self.set_headers({'User-Agent':ua.get_random_user_agent()})
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.ob[href]', 
            'title': 'a.ob[href]', 
            'text': 'p.s', 
            'links': 'ul.results-standard > li', 
            'next': {'href':'div.pagination li a[href]', 'text':'Next'}
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/search?q={}'.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = [
            i['href'] for i in tags.select(selector['href']) 
            if i.text == selector['text']
        ]
        url = (self._base_url + next_page[0]) if next_page else None
        return {'url':url, 'data':None}

