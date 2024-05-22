from src.EmailSearchEngineService import EmailSearchEngineService

def main():
    # Instantiate the EmailSearchEngineService
    email_search_service = EmailSearchEngineService()
    
    # Example inputs: Replace these with the actual inputs you want to search for
    first_name = "Ivan"
    last_name = "Law"
    company_name = "Reperio"
    
    q = first_name + ' ' + last_name + ' ' + company_name + ' email'
    # Search for email addresses using the EmailSearchEngineService
    possible_emails = email_search_service.search(q)
    
    # Print the results
    print("Possible email addresses:")
    for email in possible_emails:
        print(email)

if __name__ == "__main__":
    main()
