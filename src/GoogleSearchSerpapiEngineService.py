import requests
import SearchEngineService

class GoogleSearchSerpapiEngineService(SearchEngineService):

    def __init__(self) -> None:
        # Replace 'YOUR_SERPAPI_API_KEY' with your actual SerpApi API key
        self._api_key = '91197a6703929d2ab819231122b9db009a8cd9b846b6ef9eba160c4804b15dcf'
        # SerpApi endpoint for Google search results
        self._endpoint = 'https://serpapi.com/search'
        
    def search(self,q=""):        
        # Parameters for the search request
        params = {
            'q': q,            # The search query
            'engine': 'google',    # Search engine (e.g., google, bing, yahoo)
            'api_key': self._api_key     # Your SerpApi API key
        }
        
        try:
            # Sending GET request to SerpApi
            response = requests.get(self._endpoint, params=params)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Return the JSON response containing search results
                return response.json()
            else:
                print(f"Request failed with status code {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error occurred: {e}")
            return None
