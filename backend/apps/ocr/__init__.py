"""
OCR识别与报告生成模块

功能：
- 扫描件上传
- PaddleOCR识别
- PDF报告生成

扩展点：
- 可接入其他OCR服务
- 可添加表格识别
- 可添加手写识别
"""
default_app_config = 'apps.ocr.apps.OcrConfig'
