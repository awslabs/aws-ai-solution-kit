English | [简体中文](README_zh.md)

## Custom Template OCR sample for Health kit(Jiankang Bao)

This repo is a sample project for [AI Solution Kit](https://github.com/awslabs/aws-ai-solution-kit). The Health Kit serves as areference for assessing citizens fitness for going back to work, entering/exitingpublic places, and other situations concerning COVID-19 prevention andcontrol. In this example, we use Custom Template OCR feature to recognize and extract Simplified Chinese information such as person name, ID card, Covid status in Health kit.

### Repository Structure
```
└── src
    ├── jian-kang-bao                   Sample code for Health kit
    │   ├── jkb-create-template.ipynb   Create template
    │   ├── jkb-ocr.ipynb               OCR for Health kit
    │   ├── jkb-template.png
    │   └── jkb-test-input.png
    ├── sui-shen-ma                     Sample code for Shanghai QR Code
    │   ├── ssm-create-template.ipynb   Create template
    │   ├── ssm-ocr.ipynb               OCR for Shanghai QR Code
    │   ├── ssm-template.png
    │   └── ssm-test-input.png
    └── xing-cheng-ma                   Sample code for Trip code
        ├── xcm-create-template.ipynb   Create template
        ├── xcm-ocr.ipynb               OCR for Trip code
        ├── xcm-template.png
        └── xcm-test-input.jpeg
```

### Get started

![steps](steps.png)

- Please follow the instructions to deploy AI Solution Kit first, https://awslabs.github.io/aws-ai-solution-kit/en/
- Create OCR template with the create template Notebooks
- Run the OCR Notebooks to extract the healthy information

