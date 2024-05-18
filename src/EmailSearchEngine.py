import dns.resolver
import SearchEngineService

class EmailSearchEngineService:

    def __init__(self):
        self._search_engine_service_instance = SearchEngineService()

    def search(self, name, lastname, company):
        # Implement the search logic for company domain based on name, lastname, and company
        # This method seems incomplete, please complete the implementation based on your requirements
        pass

    def get_email_enabled(self, domain):
        try:
            # Check DNS resolution for MX (Mail Exchange) records
            dns.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            return False

    def possible_email_addresses_of_a_contact(self, first_name, last_name, company_name):
        # Retrieve company domain using SearchEngineService
        company_domain = self._search_engine_service_instance.search(company_name)
        
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
