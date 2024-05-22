from bs4 import BeautifulSoup
import requests
import editdistance

from configuration import storage_user_agent_pool_database_path
from configuration import storage_proxy_pool_database_path

from src.GoogleSearchEngine import GoogleSearchEngine
from src.GoogleSearchSerpapiEngine import GoogleSearchSerpapiEngine
from src.BingSearchEngine import BingSearchEngine
from src.YahooSearchEngine import YahooSearchEngine
from src.DuckDuckGoSearchEngine import DuckDuckGoSearchEngine
from src.StartPageSearchEngine import StartPageSearchEngine
from src.AolSearchEngine import AolSearchEngine
from src.DogpileSearchEngine import DogpileSearchEngine
from src.AskSearchEngine import AskSearchEngine
from src.MojeekSearchEngine import MojeekSearchEngine
from src.BraveSearchEngine import BraveSearchEngine
from src.TorchSearchEngine import TorchSearchEngine
from brainboost_data_source_requests_package.ProxyPool import ProxyPool
from brainboost_data_source_requests_package.UserAgentPool import UserAgentPool




import random
from urllib.parse import urlparse
from tld import get_tld

import whois
import dns.resolver

from src.GoogleSearchSerpapiEngine import GoogleSearchSerpapiEngine

class SearchEngineService:


    def __init__(self) -> None:
        user_agents = []
        file_path = storage_user_agent_pool_database_path
        
        with open(file_path, 'r') as file:
            for line in file:
                # Remove leading/trailing whitespace and add to the list
                user_agent = line.strip()
                user_agents.append(user_agent)
        self._engines_dict = { 
                    "google_search_local-Search-Engine-Scraper":GoogleSearchEngine(),
                    "bing_search_local-Search-Engine-Scraper":BingSearchEngine(),
                    "yahoo_search_local-Search-Engine-Scraper":YahooSearchEngine(),
                    "duckduckgo_search_local-Search-Engine-Scraper":DuckDuckGoSearchEngine(),
                    "startpage_search_local-Search-Engine-Scraper":StartPageSearchEngine(),
                    "aol_search_local-Search-Engine-Scraper":AolSearchEngine(),
                    "dogpile_search_local-Search-Engine-Scraper":DogpileSearchEngine(),
                    "ask_search_local-Search-Engine-Scraper":AskSearchEngine(),
                    "mojeek_search_local-Search-Engine-Scraper": MojeekSearchEngine(),
                    "brave_search_local-Search-Engine-Scraper": BraveSearchEngine(),
                    "torch_search_local-Search-Engine-Scraper": TorchSearchEngine(),
                    "google_search_serpapi": GoogleSearchSerpapiEngine()
        }
        self._proxy_pool = ProxyPool(proxy_db=storage_proxy_pool_database_path)
        self._useragent_pool = UserAgentPool(user_agents_list_path=storage_user_agent_pool_database_path)

        

        self._domain_for = {}
        pass



    def load_user_agents(self,file_path):
        try:
            with open(file_path, 'r') as f:
                user_agents = [line.strip() for line in f if line.strip()]
            return user_agents
        except Exception as e:
            print(f"Error loading user agents file: {e}")
            return []



    def get_random_user_agent(self):
        user_agents = self.load_user_agents(storage_user_agent_pool_database_path)
        return random.choice(user_agents)



    def search(self,q="",engine=None,preview=False):
        print("Executing Query: " + q)        
        if engine==None:

            # Iterate over the dictionary items
            for key, engine in self._engines_dict.items():
                try:
                    print("Searching from agent : " + key)
                    results = engine.search(q,pages=1)
                    if results:
                        links = results.links()
                        if links: 
                            return links
                    else:
                        print(key + " engine failed. Using another..")
                except:
                    print("Error using search agent: " + key)
        else:
            results = self._engines_dict[engine].search(q)
            links = results.links()
            return links
    


    def possible_email_addresses_of_a_contact(self, first_name, last_name, company_name):
        company_domain = self.get_company_domain_for(company_name)
        
        if company_domain:
            if self.get_email_enabled(company_domain):
                # Prepare email formats based on typical conventions
                possible_emails = [
                    f"{first_name.lower()}.{last_name.lower()}@{company_domain}",
                    f"{first_name.lower()[0]}{last_name.lower()}@{company_domain}",
                    f"{first_name.lower()}_{last_name.lower()}@{company_domain}",
                    f"{last_name.lower()}{first_name.lower()}@{company_domain}",
                    f"{first_name.lower()}{last_name.lower()}@{company_domain}",
                    f"{first_name.lower()}_{last_name.lower()}@{company_domain}",
                    f"{first_name.lower()}.{last_name.lower()}@{company_domain}"
                ]
            else:
                possible_emails = [
                    f"{first_name.lower()}.{last_name.lower()}@gmail.com",
                    f"{first_name.lower()[0]}{last_name.lower()}@gmail.com",
                    f"{first_name.lower()}_{last_name.lower()}@gmail.com",
                    f"{last_name.lower()}{first_name.lower()}@gmail.com",
                    f"{first_name.lower()}{last_name.lower()}@gmail.com",
                    f"{first_name.lower()}_{last_name.lower()}@gmail.com",
                    f"{first_name.lower()}.{last_name.lower()}@gmail.com",
                ]
        else:
            possible_emails = []  # Return an empty list if company_domain is None
            
        print(possible_emails)
        return possible_emails



