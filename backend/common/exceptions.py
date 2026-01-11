"""
自定义异常处理

提供统一的异常响应格式，便于前端统一处理
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    
    将所有异常转换为统一的响应格式：
    {
        "code": 错误码,
        "message": 错误信息,
        "data": null
    }
    
    Args:
        exc: 异常对象
        context: 请求上下文
        
    Returns:
        Response: 格式化的错误响应
    """
    # 先调用DRF默认的异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        # 记录异常日志
        logger.warning(
            f"API异常: {exc.__class__.__name__} - {str(exc)} - "
            f"Path: {context['request'].path}"
        )
        
        # 格式化响应
        custom_response = {
            'code': response.status_code,
            'message': _get_error_message(response.data),
            'data': None
        }
        response.data = custom_response
    else:
        # 处理未知异常
        logger.error(
            f"未处理异常: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True
        )
        return Response({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def _get_error_message(data):
    """
    从DRF错误数据中提取错误信息
    
    Args:
        data: DRF错误数据（可能是字典、列表或字符串）
        
    Returns:
        str: 格式化的错误信息
    """
    if isinstance(data, dict):
        # 处理字段错误
        messages = []
        for field, errors in data.items():
            if isinstance(errors, list):
                field_msg = ', '.join(str(e) for e in errors)
            else:
                field_msg = str(errors)
            if field == 'detail':
                messages.append(field_msg)
            elif field == 'non_field_errors':
                messages.append(field_msg)
            else:
                messages.append(f"{field}: {field_msg}")
        return '; '.join(messages)
    elif isinstance(data, list):
        return ', '.join(str(item) for item in data)
    else:
        return str(data)


class BusinessException(Exception):
    """
    业务异常基类
    
    用于处理业务逻辑中的异常情况，如权限不足、数据冲突等
    
    Attributes:
        code: 错误码
        message: 错误信息
    """
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class PermissionDeniedException(BusinessException):
    """权限不足异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, code=404)


class ValidationException(BusinessException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, code=400)
