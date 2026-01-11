"""
通用工具函数

提供各模块共用的工具方法
"""

import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional
from django.utils import timezone


def generate_uuid() -> str:
    """
    生成UUID字符串
    
    Returns:
        str: 32位UUID字符串（不含连字符）
    """
    return uuid.uuid4().hex


def generate_code(prefix: str, length: int = 8) -> str:
    """
    生成业务编码
    
    Args:
        prefix: 编码前缀，如 'WT'(委托)、'YP'(样品)
        length: 随机数部分长度
        
    Returns:
        str: 业务编码，格式如 WT20240115-ABC12345
        
    Example:
        >>> generate_code('WT')
        'WT20240115-ABC12345'
    """
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = uuid.uuid4().hex[:length].upper()
    return f"{prefix}{date_part}-{random_part}"


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 小写的扩展名（不含点号）
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def generate_file_path(category: str, filename: str) -> str:
    """
    生成文件存储路径
    
    Args:
        category: 文件分类，如 'reports'、'scans'
        filename: 原始文件名
        
    Returns:
        str: 存储路径，格式如 reports/2024/01/abc123.pdf
    """
    ext = get_file_extension(filename)
    date_path = datetime.now().strftime('%Y/%m')
    new_filename = f"{generate_uuid()}.{ext}" if ext else generate_uuid()
    return f"{category}/{date_path}/{new_filename}"


def calculate_md5(file_path: str) -> Optional[str]:
    """
    计算文件MD5值
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: MD5哈希值，文件不存在返回None
    """
    if not os.path.exists(file_path):
        return None
    
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_datetime(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        fmt: 格式字符串
        
    Returns:
        str: 格式化后的字符串
    """
    if dt is None:
        return ''
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    return dt.strftime(fmt)


def format_date(dt: datetime, fmt: str = '%Y-%m-%d') -> str:
    """
    格式化日期
    
    Args:
        dt: datetime对象
        fmt: 格式字符串
        
    Returns:
        str: 格式化后的字符串
    """
    return format_datetime(dt, fmt)


def safe_int(value, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 待转换的值
        default: 转换失败时的默认值
        
    Returns:
        int: 转换后的整数
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 待转换的值
        default: 转换失败时的默认值
        
    Returns:
        float: 转换后的浮点数
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def truncate_string(s: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断字符串
    
    Args:
        s: 原始字符串
        max_length: 最大长度
        suffix: 截断后的后缀
        
    Returns:
        str: 截断后的字符串
    """
    if not s or len(s) <= max_length:
        return s or ''
    return s[:max_length - len(suffix)] + suffix


def dict_to_choices(d: dict) -> list:
    """
    将字典转换为Django choices格式
    
    Args:
        d: 字典，key为值，value为显示名
        
    Returns:
        list: choices列表
        
    Example:
        >>> dict_to_choices({'pending': '待处理', 'done': '已完成'})
        [('pending', '待处理'), ('done', '已完成')]
    """
    return [(k, v) for k, v in d.items()]
