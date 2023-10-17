from parsers import PdfParser, TxtParser, DocParser, HtmlParser, EmailParser, ImageParser

class ParserFactory:
    @staticmethod
    def create_parser(file_type, s3_client):
        if file_type in ['.pdf', '.PDF']:
            return PdfParser(s3_client=s3_client)
        elif file_type in ['.txt', '.TXT']:
            return TxtParser(s3_client=s3_client)
        elif file_type in ['.doc', '.docx', '.DOC', '.DOCX']:
            return DocParser(s3_client=s3_client)
        elif file_type in ['.html', '.htm', '.HTML', '.HTM']:
            return HtmlParser(s3_client=s3_client)
        elif file_type in ['.eml', '.EML']:
            return EmailParser(s3_client=s3_client)
        elif file_type in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            return ImageParser(s3_client=s3_client, fd_model_path='./fd_model/', 
                               ocr_model_path='./ocr_model/')
        else:
            raise ValueError('Unsupported file type')