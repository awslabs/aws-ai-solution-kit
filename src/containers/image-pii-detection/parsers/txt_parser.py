
import os
from .parser import BaseParser

class TxtParser(BaseParser):
    def __init__(self, s3_client):
        super().__init__(s3_client=s3_client)

    def parse_file(self, txt_path):
        """
        Extracts text from a TXT file and returns a list of lines.
        """

        # Read the file
        with open(txt_path, 'r') as file:
            file_content = file.read()

        return [file_content]
