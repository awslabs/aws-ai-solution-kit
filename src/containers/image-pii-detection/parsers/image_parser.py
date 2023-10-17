
import os
from .parser import BaseParser

from PIL import Image
import numpy as np

from .image_analysis.face_detection import face_detection_main
from .image_analysis.general_ocr import ocr_main

def check_keywords_exist(det_results, keywords):
    for keyword in keywords:
        found = False
        for dt_result in det_results:
            text, score = dt_result[1]
            if keyword in text and score >= 0.5:
                found = True
                break
        if not found:
            return False
    return True
    
class ImageParser(BaseParser):
    def __init__(self, s3_client, fd_model_path, ocr_model_path):
        super().__init__(s3_client=s3_client)
        self.face_detection_model = face_detection_main.SCRFD(model_file = fd_model_path + 'det.onnx')
        self.ocr_model = ocr_main.TextSystem(model_path = ocr_model_path)
        # additional PdfParser constructor code here
    
    def read_img(self, file_path):
        img = np.array(Image.open(file_path).convert('RGB'))[:, :, :3]
        
        return img

    def face_detection_pipeline(self, img):
        bboxes, kpss = self.face_detection_model.detect(img)
        return bboxes, kpss

    def ocr_pipeline(self, img):
        img = img[:,:,::-1]
        dt_boxes, rec_res = self.ocr_model(img)
        dt_results = list(zip(dt_boxes, rec_res))
        return dt_results

    def parse_file(self, file_path):
        file_content = []
        img = self.read_img(file_path)

        face_detection_result, _ = self.face_detection_pipeline(img)
        ocr_pipeline_result = self.ocr_pipeline(img)

        contain_face = True if len(face_detection_result) > 0 else False
        business_license_keywords = ['营', '业', '执', '照', '信用代码']
        cnid_keywords = ['公', '民', '身', '份', '号', '码']
        car_license_keywords = ['机动车', '驾驶证']
        
        contain_business_license = check_keywords_exist(ocr_pipeline_result, business_license_keywords)
        contain_cnid = check_keywords_exist(ocr_pipeline_result, cnid_keywords)
        contain_car_license = check_keywords_exist(ocr_pipeline_result, car_license_keywords)
        
        if contain_face:
            if contain_cnid:
                file_content.append('ChineseID')
            elif contain_car_license:
                file_content.append('CarLicense')
            else:
                file_content.append('Face')
        else:
            if contain_business_license:
                file_content.append('BusinessLicense')
            elif contain_car_license:
                file_content.append('CarLicense')
            else:
                pass

        return file_content



