import dns.resolver
import re
from src.SearchEngineService import SearchEngineService

class EmailSearchEngineService(SearchEngineService):

    def __init__(self):
        super().__init__()


    def search(self, q="", engine=None, preview=False):
        # Perform the search using the superclass method
        search_results = super().search_with_preview(q, engine, preview)
        
        # Process the search results to extract possible email addresses
        possible_emails = self.extract_emails_from_results(search_results)
        
        return possible_emails

    def extract_emails_from_results(self, search_results):
        emails = []
        for result in search_results:
            # Check the preview text for email addresses
            preview_text = result.get('preview', '')
            emails.extend(self.extract_emails(preview_text))
        
        return emails

    def extract_emails(self, text):
        # Extract email addresses using a simple regex pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(email_pattern, text)

    def get_email_enabled(self, domain):
        try:
            # Check DNS resolution for MX (Mail Exchange) records
            dns.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            return False

    def possible_email_addresses_of_a_contact(self, first_name, last_name, company_name):
        # Retrieve company domain using SearchEngineService
        company_domain = self.search(company_name)
        
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
                # Use fallback domain (e.g., gmail.com) if company domain does not support email
                fallback_domain = 'gmail.com'
                possible_emails = [
                    f"{first_name.lower()}.{last_name.lower()}@{fallback_domain}",
                    f"{first_name.lower()[0]}{last_name.lower()}@{fallback_domain}",
                    f"{first_name.lower()}_{last_name.lower()}@{fallback_domain}",
                    f"{last_name.lower()}{first_name.lower()}@{fallback_domain}",
                    f"{first_name.lower()}{last_name.lower()}@{fallback_domain}",
                    f"{first_name.lower()}_{last_name.lower()}@{fallback_domain}",
                    f"{first_name.lower()}.{last_name.lower()}@{fallback_domain}",
                ]
        else:
            possible_emails = []  # Return an empty list if company_domain is None

        return possible_emails
