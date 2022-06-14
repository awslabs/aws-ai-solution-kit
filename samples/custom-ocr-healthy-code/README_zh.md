[English](README.md) | 简体中文

# 模版OCR轻松搞定健康码识别

## 此工程为 [AI Solution Kit](https://github.com/awslabs/aws-ai-solution-kit) 示例代码

Repo结构说明:
```
└── src
    ├── jian-kang-bao                   健康宝示例代码
    │   ├── jkb-create-template.ipynb   创建模版
    │   ├── jkb-ocr.ipynb               识别健康宝文字信息
    │   ├── jkb-template.png
    │   └── jkb-test-input.png
    ├── sui-shen-ma                     随申码示例代码
    │   ├── ssm-create-template.ipynb   创建模版
    │   ├── ssm-ocr.ipynb               识别随申码文字信息
    │   ├── ssm-template.png
    │   └── ssm-test-input.png
    └── xing-cheng-ma                   行程码示例代码
        ├── xcm-create-template.ipynb   创建模版
        ├── xcm-ocr.ipynb               识别行程码文字信息
        ├── xcm-template.png
        └── xcm-test-input.jpeg
```

使用步骤:

![steps](steps_zh.png)

- 部署AI Solution Kit解决方案：请参考 [AI Solution Kit 实施指南](https://awslabs.github.io/aws-ai-solution-kit/zh/) 
- 创建模版：请执行对应示例代码中的创建模版示例
- 文字识别：在创建好模版后，根据生成的模版ID，执行对应文件夹下的识别文字信息示例

