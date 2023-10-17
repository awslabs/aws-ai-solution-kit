
import os
import boto3
from pypdf import PdfReader

from .parser import BaseParser

class PdfParser(BaseParser):
    def __init__(self, s3_client):
        super().__init__(s3_client=s3_client)
    

    def parse_file(self, pdf_path):
        """
        Extracts text from a PDF file and returns a list of lines.
        """

        # Create a PDF reader object
        pdf_reader = PdfReader(pdf_path)
        file_content = []

        # Loop through each page in the PDF file
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]

            # Extract the text from the page and append it to the string
            page_content = page.extract_text()
            file_content.append(page_content)

        return file_content
