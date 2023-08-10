AI ​​Solution Kit provides a series of machine learning functions based on deep learning, such as text recognition,
natural language understanding, face detection, and image understanding. You can easily use out-of-the-box AI features
by calling APIs, while seamlessly integrating with other services provided by AWS.

## APIs

The solution automatically creates RESTful APIs through Amazon API Gateway.
After [deploying the solution](./deployment.md), you can send HTTP POST requests to use the AI features.

The table below lists the supported APIs. You can click the **Details** link to view the test method and sample code of
each API interface. For more information, see [API Reference Guide](./api-explorer.md).

### Optical Character Recognition (OCR)

| **API Name**                      | **Description**                                                                                                                                                                                | API                                          |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| Lite OCR (Simplified Chinese)     | Recognize and extract Simplified Chinese, numbers, alphabetical characters and symbols. Return the information such as text or coordinates.                                                    | [Details](deploy-general-ocr.md)             |
| General OCR (Traditional Chinese) | Recognize and extract Traditional Chinese, numbers, alphabetical characters and symbols from images. Return the information such as text or coordinates.                                       | [Details](deploy-general-ocr-traditional.md) |
| Advanced OCR (Multi-Languages)    | Recognize and extract Simplified/Traditional Chinese, Vietnamese, Japanese, Korean, English, numbers, alphabetical characters and symbols. Return the information such as text or coordinates. | [Details](deploy-advanced-ocr.md)            |
| Custom OCR                        | You can customize the OCR template, extract the structured text information in cards and tickets, and display the results in the key-value format.                                             | [Details](deploy-custom-ocr.md)              |
| Car License Plate                 | Recognize text on Chinese car license plate.                                                                                                                                                   | [Details](deploy-car-license-plate.md)       |

### Face and Body

| **API Name**                | **Description**                                                                                                                                                                                                                     | API                                              |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| Face Detection              | Detect the face in an image, and map the detected facial features and contour key point information to 64 vector coordinates.                                                                                                       | [Details](deploy-face-detection.md)              |
| Face Comparison             | Compare two faces of the same person and return a confidence score of the similarity.                                                                                                                                               | [Details](deploy-face-comparison.md)             |
| Human Attribute Recognition | Recognize the attributes of the human body in the image, and return the human body position coordinates and attribute analysis in each area, including the semantic information of 16 attributes such as gender, age, and clothing. | [Details](deploy-human-attribute-recognition.md) |
| Human Image Segmentation    | Segment human bodies from background and return the alpha channel which is a color component representing the degree of transparency of a color.                                                                                    | [Details](deploy-human-image-segmentation.md)    |

### Image Understanding

| **API Name**          | **Description**                                                                                                                                     | API                                        |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| Image Similarity      | Compare two images by calculating the cosine distance from the image feature vector and converting it into confidence, and return similarity score. | [Details](deploy-text-similarity.md)       |
| Object Recognition    | Recognize objects in the image and return the region information and confidence score for each object. 300 types of objects are supported.          | [Details](deploy-object-recognition.md)    |
| Pornography Detection | Detect pornographic image in three dimensions (normal, sexy, porn) and return confidence scores.                                                    | [Details](deploy-pornography-detection.md) |

### Vision Production

| **API Name**           | **Description**                                           | API                                         |
|------------------------|-----------------------------------------------------------|---------------------------------------------|
| Image Super Resolution | Upscale the resolution and enhance details in the images. | [Details](deploy-image-super-resolution.md) |

### Natural Language Understanding (NLU)

| **API Name**    | **Description**                                                                                                                                        | API                                  |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| Text Similarity | Compare two Chinese words or sentences and return similarity score.                                                                                    | [Details](deploy-text-similarity.md) |
| General NLG     | Support a variety of Chinese text understanding tasks, such as text classification, sentiment analysis, extraction, and customizable labeling systems. | [Details](deploy-general-nlu.md)     |

This implementation guide describes architectural considerations and configuration steps for deploying AI Solution Kit
in the AWS cloud. It includes links to CloudFormation templates that launches and configures the AWS services required
to deploy this solution using AWS best practices for security and availability.

The guide is intended for IT architects, developers, DevOps, data engineers with practical experience architecting in
the AWS Cloud.




<!--
### **语音技术**
|    **名称**   | **描述**    | **部署说明** |
|--------------|------------|-------------|
|||
-->