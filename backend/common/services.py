"""
第三方服务接口适配层

所有第三方服务的调用都通过这里进行封装
后续只需修改此文件即可切换服务实现
"""

import logging
from typing import Optional, Dict, Any, List
from django.conf import settings

logger = logging.getLogger(__name__)


# ==================== MinIO 对象存储服务 ====================

class MinIOService:
    """
    MinIO对象存储服务
    
    提供文件上传、下载、删除等功能
    
    扩展点：
    - 可替换为阿里云OSS、腾讯云COS等
    - 修改 _get_client 方法和相关操作即可
    
    Attributes:
        client: MinIO客户端实例
        bucket_name: 存储桶名称
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.client = None
        self.bucket_name = settings.MINIO_CONFIG.get('BUCKET_NAME', 'lims-files')
        self._init_client()
    
    def _init_client(self):
        """
        初始化MinIO客户端
        
        如需切换存储服务，修改此方法
        """
        try:
            from minio import Minio
            self.client = Minio(
                settings.MINIO_CONFIG.get('ENDPOINT'),
                access_key=settings.MINIO_CONFIG.get('ACCESS_KEY'),
                secret_key=settings.MINIO_CONFIG.get('SECRET_KEY'),
                secure=settings.MINIO_CONFIG.get('SECURE', False)
            )
            # 确保bucket存在
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
            logger.info(f"MinIO客户端初始化成功: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"MinIO客户端初始化失败: {e}")
            self.client = None
    
    def upload_file(self, file_path: str, object_name: str, content_type: str = None) -> Optional[str]:
        """
        上传文件
        
        Args:
            file_path: 本地文件路径
            object_name: 对象存储中的文件名
            content_type: 文件MIME类型
            
        Returns:
            str: 文件访问URL，失败返回None
        """
        if not self.client:
            logger.error("MinIO客户端未初始化")
            return None
        
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type=content_type
            )
            return f"{settings.MINIO_CONFIG.get('ENDPOINT')}/{self.bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return None
    
    def upload_bytes(self, data: bytes, object_name: str, content_type: str = None) -> Optional[str]:
        """
        上传字节数据
        
        Args:
            data: 文件字节数据
            object_name: 对象存储中的文件名
            content_type: 文件MIME类型
            
        Returns:
            str: 文件访问URL，失败返回None
        """
        if not self.client:
            return None
        
        try:
            from io import BytesIO
            data_stream = BytesIO(data)
            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                len(data),
                content_type=content_type
            )
            return f"{settings.MINIO_CONFIG.get('ENDPOINT')}/{self.bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"字节数据上传失败: {e}")
            return None
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        """
        下载文件
        
        Args:
            object_name: 对象存储中的文件名
            
        Returns:
            bytes: 文件字节数据，失败返回None
        """
        if not self.client:
            return None
        
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """
        删除文件
        
        Args:
            object_name: 对象存储中的文件名
            
        Returns:
            bool: 删除是否成功
        """
        if not self.client:
            return False
        
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """
        获取预签名URL
        
        Args:
            object_name: 对象存储中的文件名
            expires: URL有效期（秒）
            
        Returns:
            str: 预签名URL，失败返回None
        """
        if not self.client:
            return None
        
        try:
            from datetime import timedelta
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except Exception as e:
            logger.error(f"获取预签名URL失败: {e}")
            return None


# ==================== OCR 识别服务 ====================

class OCRService:
    """
    OCR识别服务
    
    提供图片文字识别功能，默认使用PaddleOCR
    
    扩展点：
    - 可替换为百度OCR、阿里云OCR等
    - 修改 recognize 方法即可
    """
    
    def __init__(self):
        self.enabled = settings.OCR_CONFIG.get('ENABLED', False)
        self.api_url = settings.OCR_CONFIG.get('API_URL')
    
    def recognize(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径或URL
            
        Returns:
            dict: 识别结果，包含文字内容和位置信息
            {
                'success': True,
                'text': '识别的文字',
                'details': [
                    {'text': '单行文字', 'confidence': 0.99, 'position': [...]}
                ]
            }
        """
        if not self.enabled:
            logger.warning("OCR服务未启用")
            return {'success': False, 'message': 'OCR服务未启用'}
        
        try:
            import requests
            response = requests.post(
                f"{self.api_url}/ocr",
                json={'image': image_path},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'message': f'OCR服务返回错误: {response.status_code}'}
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def recognize_table(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        识别图片中的表格
        
        Args:
            image_path: 图片文件路径或URL
            
        Returns:
            dict: 表格识别结果
        """
        if not self.enabled:
            return {'success': False, 'message': 'OCR服务未启用'}
        
        try:
            import requests
            response = requests.post(
                f"{self.api_url}/table",
                json={'image': image_path},
                timeout=60
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'message': f'表格识别返回错误: {response.status_code}'}
        except Exception as e:
            logger.error(f"表格识别失败: {e}")
            return {'success': False, 'message': str(e)}


# ==================== AI 大模型服务 ====================

class AIService:
    """
    AI大模型服务
    
    提供文档校验、智能问答等功能
    
    扩展点：
    - 支持本地Ollama、OpenAI、讯飞星火等
    - 通过配置切换不同的模型
    """
    
    def __init__(self):
        self.enabled = settings.AI_CONFIG.get('ENABLED', False)
        self.api_url = settings.AI_CONFIG.get('API_URL')
        self.model_name = settings.AI_CONFIG.get('MODEL_NAME')
        self.api_key = settings.AI_CONFIG.get('API_KEY')
    
    def verify_document(self, content: str, rules: List[str] = None) -> Dict[str, Any]:
        """
        校验文档内容
        
        Args:
            content: 文档内容
            rules: 校验规则列表
            
        Returns:
            dict: 校验结果
            {
                'success': True,
                'issues': [
                    {'type': 'typo', 'position': 10, 'original': '错字', 'suggestion': '正确字'}
                ],
                'summary': '发现3处问题'
            }
        """
        if not self.enabled:
            return {'success': False, 'message': 'AI服务未启用'}
        
        prompt = f"""请检查以下文档内容，找出其中的错别字、语法错误和数据不合理之处：

{content}

请以JSON格式返回检查结果，包含以下字段：
- issues: 问题列表，每个问题包含type(问题类型)、position(位置)、original(原文)、suggestion(建议)
- summary: 问题总结
"""
        
        return self._chat(prompt)
    
    def check_data_validity(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查数据合理性
        
        Args:
            data: 待检查的数据
            rules: 检查规则
            
        Returns:
            dict: 检查结果
        """
        if not self.enabled:
            return {'success': False, 'message': 'AI服务未启用'}
        
        prompt = f"""请根据以下规则检查数据的合理性：

数据：
{data}

规则：
{rules}

请判断数据是否符合规则，并给出检查结果。
"""
        
        return self._chat(prompt)
    
    def _chat(self, prompt: str) -> Dict[str, Any]:
        """
        调用大模型进行对话
        
        Args:
            prompt: 提示词
            
        Returns:
            dict: 模型响应
        """
        try:
            import requests
            
            # Ollama API格式
            if 'ollama' in self.api_url or '11434' in self.api_url:
                response = requests.post(
                    f"{self.api_url}/api/generate",
                    json={
                        'model': self.model_name,
                        'prompt': prompt,
                        'stream': False
                    },
                    timeout=120
                )
            else:
                # OpenAI兼容格式
                headers = {}
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                response = requests.post(
                    f"{self.api_url}/v1/chat/completions",
                    headers=headers,
                    json={
                        'model': self.model_name,
                        'messages': [{'role': 'user', 'content': prompt}]
                    },
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                return {'success': True, 'data': result}
            else:
                return {'success': False, 'message': f'AI服务返回错误: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"AI服务调用失败: {e}")
            return {'success': False, 'message': str(e)}


# ==================== 服务实例 ====================

# 单例模式获取服务实例
def get_minio_service() -> MinIOService:
    """获取MinIO服务实例"""
    return MinIOService()


def get_ocr_service() -> OCRService:
    """获取OCR服务实例"""
    return OCRService()


def get_ai_service() -> AIService:
    """获取AI服务实例"""
    return AIService()
