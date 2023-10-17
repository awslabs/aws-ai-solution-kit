import os
import magic
import re
from tempfile import NamedTemporaryFile


class BaseParser:
    def __init__(self, s3_client):
        # constructor code here
        # self.region = region
        self.s3_client=s3_client
        pass

    def parse_file(self, file_path, **kwargs):
        """This method must be overwritten by child classes to extract raw
        text from a file path. 
        """
        raise NotImplementedError('must be overwritten by child classes')

    def load_content(self, bucket, object_key):
        """
        Downloads the file from S3.
        """
        # Create a temporary file
        with NamedTemporaryFile() as temp_file:
            self.s3_client.download_file(Bucket=bucket, Key=object_key, Filename=temp_file.name)
            file_path = temp_file.name

            file_content = self.parse_file(file_path)
            processed_content = self.postprocess_content(file_content)

        return processed_content
    
    def postprocess_content(self, file_content):
        """
        For each item in content, if size is bigger than 128, split it into multiple items.
        """
        # split all_page_content into a list of lines and remove empty lines
        processed_content=[]
        for page in file_content:
            # page_content = []
            lines = [line for line in page.splitlines() if line.strip() != '']

            for item in lines:
                if len(item) > 128:
                    # Split item by . and extend to processed_content
                    split_items = re.split(r'(?<=[.。;])', item)
                    # 
                    for split_item in split_items:
                        if len(split_item) != 0:
                            # Avoid too long item
                            processed_content.append(split_item[:256])
                else:
                    processed_content.append(item)

        return processed_content

    def get_encoding(self, file_path):
        """
        Returns the encoding of the file.
        """
        blob = open(file_path, 'rb').read()
        m = magic.Magic(mime_encoding=True)
        encoding = m.from_buffer(blob)
        return encoding