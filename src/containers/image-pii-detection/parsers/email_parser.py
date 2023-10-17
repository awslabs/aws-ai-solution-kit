
import os
from .parser import BaseParser
from email.parser import Parser as PyEmailParser

class EmailParser(BaseParser):
    def __init__(self, s3_client):
        super().__init__(s3_client=s3_client)


    def parse_file(self, eml_path):
        """
        Extracts text from a eml file and returns a string of content.
        """

        with open(eml_path) as stream:
            parser = PyEmailParser()
            message = parser.parse(stream)

        file_content = []
        for part in message.walk():
            if part.get_content_type().startswith('text/plain'):
                file_content.append(part.get_payload())

        return ['\n'.join(file_content)]
