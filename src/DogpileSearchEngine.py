from src.SearchEngine import SearchEngine
from brainboost_data_source_requests_package.UserAgentPool import UserAgentPool

from src.utils import unquote_url
from configuration import storage_user_agent_pool_database_path

class DogpileSearchEngine(SearchEngine):
    '''Seaches dogpile.com'''
    def __init__(self, proxy=None, timeout=10):
        super(DogpileSearchEngine, self).__init__(proxy, timeout)
        self._base_url = 'https://www.dogpile.com'
        uap = UserAgentPool(user_agents_list_path=storage_user_agent_pool_database_path)
        self.set_headers({'User-Agent':uap.get_random_user_agent()})
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[class$=title]', 
            'title': 'a[class$=title]', 
            'text': {'tag':'span', 'index':-1}, 
            'links': 'div[class^=web-] div[class$=__result]', 
            'next': 'a.pagination__num--next'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/serp?q={}'.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return {'url':url, 'data':None}

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        selector = self._selectors('text')
        tag = tag.select(selector['tag'])[selector['index']]
        return self._get_tag_item(tag, 'text')

    
