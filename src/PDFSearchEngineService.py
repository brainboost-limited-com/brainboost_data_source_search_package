import os

import pypdf

import SearchEngineService

class PDFSearchEngineService(SearchEngineService):


    def __init__(self,directory) -> None:
        self.path = directory
        super().__init__()


    def search(self,q="",engine=None, preview=False):
        results = []

        # Iterate over all files in the directory
        for filename in os.listdir(self.path):
            filepath = os.path.join(self.path, filename)
            
            # Check if the file is a PDF
            if filepath.endswith('.pdf'):
                try:
                    with open(filepath, 'rb') as pdf_file:
                        pdf_reader = pypdf.PdfReader(pdf_file)
                        num_pages = pdf_reader.get_num_pages()  # Assuming getNumPages exists

                        # Iterate through each page of the PDF
                        for page_num in range(num_pages):
                            page = pdf_reader.get_page(page_num)
                            text = page.extract_text()
                            
                            # Check if the search text is present in the current page
                            if q in text:
                                results.append({
                                    'file': filename,
                                    'page': page_num + 1  # Page numbers are 1-based
                                })
                except pypdf.errors.PyPdfError:
                    # Handle any unreadable PDF files
                    print(f"Error reading PDF: {filepath}")
        
        return results
