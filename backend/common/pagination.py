"""
自定义分页器

提供统一的分页响应格式，支持前端分页组件
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    标准分页器
    
    支持以下查询参数：
    - page: 页码，默认1
    - page_size: 每页数量，默认20，最大100
    
    响应格式：
    {
        "code": 200,
        "message": "success",
        "data": {
            "total": 100,
            "page": 1,
            "page_size": 20,
            "results": [...]
        }
    }
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        返回统一格式的分页响应
        
        Args:
            data: 序列化后的数据列表
            
        Returns:
            Response: 包含分页信息的响应对象
        """
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'results': data
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    大数据集分页器
    
    用于数据量较大的查询场景，每页最多500条
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
