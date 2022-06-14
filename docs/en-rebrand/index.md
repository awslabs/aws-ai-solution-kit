AI ​​Solution Kit provides a series of machine learning functions based on deep learning, such as text recognition, natural language understanding, face detection, and image understanding. You can easily use out-of-the-box AI features by calling APIs, while seamlessly integrating with other services provided by Amazon Web Services.

## APIs

The solution automatically creates RESTful APIs through Amazon API Gateway. After [deploying the solution](./deployment.md), you can send HTTP POST requests to use the AI features. 

The table below lists the supported APIs. You can click the **Details** link to view the test method and sample code of each API interface. For more information, see [API Reference Guide](./api-explorer.md).


### Optical Character Recognition (OCR)
|    **API Name**   | **Description**    | API |
|--------------|------------|-------------|
|General OCR (Simplified Chinese)|Recognize and extract Simplified Chinese, numbers, alphabetical characters and symbols from images, and return information such as coordinates and confidence.|[Details](deploy-general-ocr.md)|
|General OCR (Traditional Chinese)|Recognize and extract Traditional Chinese, numbers, alphabetical characters and symbols from images, and return information such as coordinates and confidence.|[Details](deploy-general-ocr-traditional.md)|
|Custom OCR|Recognize and extract structured text by predefined OCR templates.|[Details](deploy-custom-ocr.md)|
|Car License Plate|Recognize text on Chinese car license plate.|[Details](deploy-car-license-plate.md)|

### Face and Body
|    **API Name**   | **Description**    | API |
|--------------|------------|-------------|
|Face Detection|Detect the face in an image and return coordinate information of the face.|[Details](deploy-face-detection.md)|
|Face Comparison|Compare two faces of the same person and return a confidence score of the similarity.|[Details](deploy-face-comparison.md)|
|Human Attribute Recognition |Recognize the attributes of the human body in an image, such as gender and age.|[Details](deploy-human-attribute-recognition.md)|
|Human Image Segmentation|Segment human bodies from the image background.|[Details](deploy-human-image-segmentation.md)|

### Image Understanding
|    **API Name**   | **Description**    | API |
|--------------|------------|-------------|
|Image Similarity|Compare two images and return similarity score.|[Details](deploy-text-similarity.md)|
|Object Recognition|Recognize objects and scenes in an image and return confidence score for each object or scene.|[Details](deploy-object-recognition.md)|
|Pornography Detection|Detect pornographic image in three dimensions (normal, sexy, porn) and return confidence scores.|[Details](deploy-pornography-detection.md)|

### Vision Production
|    **API Name**   | **Description**    | API |
|--------------|------------|-------------|
|Image Super Resolution|Upscale the resolution and enhance details in the images|[Details](deploy-image-super-resolution.md)|

### Natural Language Understanding (NLU)
|    **API Name**   | **Description**    | API |
|--------------|------------|-------------|
|Text Similarity|Compare two Chinese words or sentences and return similarity score|[Details](deploy-text-similarity.md)|


This implementation guide describes architectural considerations and configuration steps for deploying AI Solution Kit in the Amazon Web Services cloud. It includes links to CloudFormation templates that launches and configures the Amazon services required to deploy this solution using Amazon Web Services best practices for security and availability.

The guide is intended for IT architects, developers, DevOps, data engineers with practical experience architecting in the Amazon Web Services Cloud.




<!--
### **语音技术**
|    **名称**   | **描述**    | **部署说明** |
|--------------|------------|-------------|
|||
-->