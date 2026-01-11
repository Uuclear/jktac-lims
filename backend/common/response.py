"""
统一响应格式

提供标准化的API响应格式
"""

from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="success", code=200):
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        code: 状态码，默认200
        
    Returns:
        Response: 格式化的成功响应
        
    Example:
        return success_response({'user': user_data}, '获取成功')
    """
    return Response({
        'code': code,
        'message': message,
        'data': data
    }, status=status.HTTP_200_OK)


def created_response(data=None, message="创建成功"):
    """
    创建成功响应
    
    Args:
        data: 创建的数据
        message: 成功消息
        
    Returns:
        Response: 格式化的创建成功响应
    """
    return Response({
        'code': 201,
        'message': message,
        'data': data
    }, status=status.HTTP_201_CREATED)


def error_response(message="操作失败", code=400, data=None):
    """
    错误响应
    
    Args:
        message: 错误消息
        code: 错误码，默认400
        data: 额外的错误信息
        
    Returns:
        Response: 格式化的错误响应
    """
    http_status = status.HTTP_400_BAD_REQUEST
    if code == 401:
        http_status = status.HTTP_401_UNAUTHORIZED
    elif code == 403:
        http_status = status.HTTP_403_FORBIDDEN
    elif code == 404:
        http_status = status.HTTP_404_NOT_FOUND
    elif code >= 500:
        http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return Response({
        'code': code,
        'message': message,
        'data': data
    }, status=http_status)


def paginated_response(paginator, data, request):
    """
    分页响应
    
    Args:
        paginator: 分页器实例
        data: 数据列表
        request: 请求对象
        
    Returns:
        Response: 格式化的分页响应
    """
    page = paginator.paginate_queryset(data, request)
    if page is not None:
        return paginator.get_paginated_response(page)
    return success_response(data)
