from src.SearchEngine import SearchEngine
from brainboost_data_source_requests_package.UserAgentPool import UserAgentPool
from src.utils import unquote_url, quote_url

class DuckduckgoSearchEngine(SearchEngine):
    '''Searches duckduckgo.com'''
    def __init__(self, proxy=None, timeout=10):
        super(DuckduckgoSearchEngine, self).__init__(proxy, timeout)
        self._base_url = 'https://html.duckduckgo.com'
        self._current_page = 1
        uap = UserAgentPool()
        self.set_headers({'User-Agent':uap.get_random_user_agent()})

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__a', 
            'title': 'a.result__a', 
            'text': 'a.result__snippet',
            'links': 'div#links div.result',
            'next': 'input[value="next"]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/html/?q={}'.format(self._base_url, quote_url(self._query, ''))
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        self._current_page += 1
        selector = self._selectors('next').format(page=self._current_page)
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = self._base_url + next_page
        return {'url':url, 'data':None}

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        selector = self._selectors('url')
        url = self._get_tag_item(tag.select_one(selector), item)

        if url.startswith(u'/url?q='):
            url = url.replace(u'/url?q=', u'').split(u'&sa=')[0]
        return unquote_url(url)
