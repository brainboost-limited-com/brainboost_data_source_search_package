import json
import os
from tqdm import tqdm
from src.brainboost_data_source_processing.JSonProcessor import JSonProcessor
from src.brainboost_data_source_search.CompanyDomainSearchEngineService import CompanyDomainSearchEngineService
from tinydb import TinyDB, Query

json_processor = JSonProcessor()
search_engine = CompanyDomainSearchEngineService()
data_source = 'resources/resources_data/data_subjective'

def get_companies(contacts):
    return json_processor.collect_values_of_particular_key_to_set(json_array=contacts, key='company')

def process_company_domains(companies, search_engine, db):
    with tqdm(total=len(companies), desc="Processing Companies") as pbar:
        for company in companies:
            if company.strip():  # Check if company name is not empty or only whitespace
                existing_record = db.search(Query().company == company)

                if not existing_record:  # Insert only if the company does not exist in the database
                    domain = search_engine.search(company)
                    db.insert(dict({'company': company, 'domain': domain}))  # Store company and domain in TinyDB

            pbar.update(1)

def save_company_domains_to_json(db, output_file):
    with open(output_file, 'w') as f:
        json.dump(db.all(), f)
        
if __name__ == "__main__":
    # Load JSON files recursively
    contacts = json_processor.load_json_files_recursively(from_path=data_source)
    
    # Extract unique company names
    companies = get_companies(contacts=contacts)
    
    # Create/open TinyDB database
    db = TinyDB('resources/resources_data/data_subjective/company_domains.json')
    
    # Process company domains with progress bar and store in TinyDB
    process_company_domains(companies, search_engine, db)
    
    # Define output file path for JSON backup (optional)
    output_file = 'resources/companies.json'
    
    # Save company domains to JSON file (backup, not necessary if using TinyDB)
    save_company_domains_to_json(db, output_file)
    
    print(f"Company domains processed and saved to TinyDB")

# To resume processing if interrupted, you can load the existing TinyDB database:
# db = TinyDB('company_domains.json')
# existing_company_domains = db.all()
# Then, continue processing or use the data as needed.
