import re
import subprocess
import Levenshtein
import dns
import editdistance
from urllib.parse import urlparse
from tinydb import TinyDB, Query
import SearchEngineService
import tldextract
import dns.resolver

class CompanyDomainSearchEngineService(SearchEngineService):


    def __init__(self) -> None:
        super().__init__()
        self._search_engine_service = SearchEngineService()
        self._db = TinyDB('src/brainboost_data_source_search/brainboost_data_source_search_resultsdatabase/company_domains.json')

    # ================================== CACHE ============================================

    def _insert_cache_domain(self, company_name, domain,id=None):
        company_name_normalized = self.normalize_company_name(company_name=company_name)
        # Create a new document with the company name and domain
        new_company_domain = {'company_name': company_name_normalized, 'domain': domain}
        
        try:
            # Attempt to insert the new document into the database
            if id != None:
                new_company_domain['id'] = len(self._db) + 2
            else:
                new_company_domain['id'] = len(self._db) + 1
            inserted_doc_id = self._db.insert(dict(new_company_domain))
            inserted_doc = self._db.get(doc_id=inserted_doc_id)
            print(f"Inserted domain for company '{company_name_normalized}': {domain}")
            return inserted_doc
        
        except ValueError as e:
            # Handle the case where a document with the same ID already exists
            self._insert_cache_domain(company_name_normalized=company_name_normalized,domain=domain,id=new_company_domain['id'])
            print(f"Error inserting domain for company '{company_name_normalized}': {domain}")
            print(f"Error message: {e}")
            return None





    def _get_cached_domain(self,company_name):
        company_name_normalized = self.normalize_company_name(company_name=company_name)
        query = Query()
        existing_doc = self._db.get(query.company_name == company_name_normalized)        
        return existing_doc

    # ===================================== SEARCH =========================================
    
    def get_domain_extensions(self):
        return [".com", ".net", ".org", ".io", ".co", ".ai"]

    def get_domain_extensions_for_country(self, country_name):
        if country_name is not None:
            country_extensions = {
                "united states": ".com",
                "united kingdom": ".co.uk",
                "germany": ".de",
                "france": ".fr",
                "japan": ".jp",
                "australia": ".au",
                "canada": ".ca",
                # Add more country-to-extension mappings as needed
            }
            country_name_lower = country_name.lower()
            return country_extensions.get(country_name_lower, None)
        else:
            return None

    def get_company_domain_in_case_of_possible_default_extension(self, company_name=None):
        normalized_company_name = self.normalize_company_name(company_name=company_name)
        extensions = self.get_domain_extensions()
        for domain_extension in extensions:
            possible_domain = normalized_company_name + domain_extension
            if self.domain_exists(possible_domain):
                return possible_domain
        return None

    def get_company_domain_in_case_of_an_specific_country(self, company_name, country):
        normalized_company_name = company_name.replace(" ", "").lower()
        extension = self.get_domain_extensions_for_country(country)
        if extension:
            possible_domain = normalized_company_name + extension
            if self.domain_exists(possible_domain):
                return possible_domain
        return self.get_company_domain_in_case_of_possible_default_extension(company_name=company_name)

    def get_company_domain_in_case_no_country_specific_not_default_extension(self,company_name):
        print("No existing domain found, searching using search engines...")
        links = super().search(company_name)
        if not links:
            print("Possibly a network issue, as no search engine worked due to block.")
            return None
        else:
            filtered_links_that_exist = [l for l in links if self.domain_exists(l)]
            if filtered_links_that_exist:
                company_domain = self.find_best_matching_domain(company_name, filtered_links_that_exist)
                if company_domain:
                    self._insert_cache_domain(company_name, company_domain)
                    return company_domain


    def domain_exists(self, url_or_domain):
        # Check if the input is a URL
        if '://' in url_or_domain:
            # Extract domain from the URL
            domain = tldextract.extract(url_or_domain).registered_domain
        else:
            # Use the input as the domain name
            domain = url_or_domain

        try:
            # Resolve the domain name for A records
            answers = dns.resolver.resolve(domain, 'A')
            return True if answers else False
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            return False
    
    def normalize_company_name(self,company_name):
        # Convert to lowercase and remove special characters
        return re.sub(r'[^a-zA-Z0-9\s]', '', company_name).lower().strip().replace(' ','')    


    def find_best_matching_domain(self,company_name, links):

        def extract_domain(url):
            parsed_url = urlparse(url)
            if parsed_url.netloc:
                return parsed_url.netloc
            return None
        

        normalized_company_name = self.normalize_company_name(company_name)
        matching_domain = None
        min_distance = float('inf')

        for url in links:
            domain = extract_domain(url)
            if domain:
                # Calculate the Levenshtein distance using the Levenshtein package
                distance = Levenshtein.distance(normalized_company_name, domain)
                if distance < min_distance:
                    matching_domain = domain
                    min_distance = distance

        return matching_domain


    def get_whois_info(self,domain):
        
        def parse_whois_data(whois_text):
            """
            This function parses WHOIS data text and extracts contact information.

            Args:
                whois_text: The WHOIS data text obtained from 'whois' command.

            Returns:
                A dictionary containing extracted information keys:
                    * phone: Phone number(s) (list of strings) (Optional)
                    * email: Email address(es) (list of strings)
                    * country: Country (string)
                    * company: Company name (string)
                    * organization: Organization name (string)
                    * state: State/Province (string)
            """
            info = {}

            # Extract Email Addresses
            info["email"] = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', whois_text)

            # Extract Country
            country_match = re.search(r"Country: (.*?)\n", whois_text, re.IGNORECASE)
            if country_match:
                info["country"] = country_match.group(1).strip()

            # Extract Company/Organization
            company_match = re.search(r"(Registrant Organization|Registrant Name): (.*?)\n", whois_text, re.IGNORECASE)
            if company_match:
                info["company"] = company_match.group(2).strip()

            # Use company name as organization
            info["organization"] = info.get("company")

            # Extract State/Province
            state_match = re.search(r"\bState/Province: (.*?)\n", whois_text, re.IGNORECASE)
            if state_match:
                info["state"] = state_match.group(1).strip()

            # Extract Phone Numbers based on contextual cues
            phone_numbers = []

            # Define regex pattern to match valid phone numbers with country code
            phone_pattern = r'\+\d{1,3}(?:\.\d+)?(?:[\s.-]?\d+)+'

            # Find all phone numbers using the defined pattern
            phone_matches = re.findall(phone_pattern, whois_text)
            
            # Filter and deduplicate phone numbers
            for phone in phone_matches:
                cleaned_phone = re.sub(r'[\s.-]', '', phone)  # Remove spaces, dots, and dashes
                if cleaned_phone not in phone_numbers:
                    phone_numbers.append(cleaned_phone)

            if phone_numbers:
                info["phone"] = phone_numbers

            return info


        try:
            # Execute whois command with capture (to get output)
            whois_result = subprocess.run(["whois", domain], capture_output=True, text=True)
            
            # Check for successful execution
            if whois_result.returncode == 0:
                return parse_whois_data(whois_result.stdout)
            else:
                print(f"Error retrieving WHOIS info for {domain} (exit code: {whois_result.returncode})")
                return None
        except subprocess.CalledProcessError as e:
            print(f"Error executing whois command: {e}")
            return None

    def extract_domain_and_extension(self, url):
        if url is not None and 'http' in url:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                return domain
            except Exception:
                return url
        else:
            return url


    def search(self, company_name=None, country=None):
        if company_name != None:
            company_name_normalized = self.normalize_company_name(company_name)
            cached_domain = self._get_cached_domain(company_name_normalized)
            if cached_domain:
                return cached_domain
            else:                
                company_domain_default_extension = self.get_company_domain_in_case_of_possible_default_extension(company_name=company_name_normalized)
                if company_domain_default_extension:
                    self._insert_cache_domain(company_name_normalized, company_domain_default_extension)
                    print('Found domain with default extension for ' + str(company_domain_default_extension))
                    return company_domain_default_extension
                if country != None: 
                    company_domain_specific_country = self.get_company_domain_in_case_of_an_specific_country(company_name=company_name_normalized, country=country)
                    if company_domain_specific_country:
                        self._insert_cache_domain(company_name_normalized, company_domain_specific_country)
                        print('Found domain with default extension for specific country ' + str(company_domain_specific_country))
                        return company_domain_specific_country
                best_domain_candidate = self.get_company_domain_in_case_no_country_specific_not_default_extension(company_name=company_name)
                if best_domain_candidate!=None:
                    print('Found domain with default extension for specific country ' + str(best_domain_candidate))
                    return best_domain_candidate
                else:
                    invented_domain = company_name_normalized+'.com'
                    return invented_domain

# ==========================================================================================================================