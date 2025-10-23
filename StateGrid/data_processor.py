from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models import GridData, db
from config import Config
import json

class DataProcessor:
    """
    数据处理类
    负责查询、筛选和转换数据为国网平台要求的格式
    """
    
    @staticmethod
    def query_data(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        data_types: Optional[List[str]] = None,
        device_ids: Optional[List[str]] = None,
        limit: int = None,
        offset: int = 0,
        status: str = '未上传'
    ) -> List[GridData]:
        """
        查询符合条件的电网数据
        
        参数:
            start_time: 开始时间
            end_time: 结束时间
            data_types: 数据类型列表
            device_ids: 设备ID列表
            limit: 返回数据条数
            offset: 偏移量
            status: 数据状态
            
        返回:
            符合条件的GridData对象列表
        """
        # 构建查询
        query = GridData.query
        
        # 时间范围筛选
        if start_time:
            query = query.filter(GridData.timestamp >= start_time)
        if end_time:
            query = query.filter(GridData.timestamp <= end_time)
        
        # 数据类型筛选
        if data_types:
            query = query.filter(GridData.data_type.in_(data_types))
        
        # 设备ID筛选
        if device_ids:
            query = query.filter(GridData.device_id.in_(device_ids))
        
        # 状态筛选
        if status:
            query = query.filter(GridData.status == status)
        
        # 排序和分页
        query = query.order_by(GridData.timestamp.desc())
        
        if limit is not None:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        # 执行查询
        return query.all()
    
    @staticmethod
    def convert_to_grid_format(data_list: List[GridData]) -> List[Dict[str, Any]]:
        """
        将数据列表转换为国网平台要求的格式
        
        参数:
            data_list: GridData对象列表
            
        返回:
            符合国网平台格式的数据字典列表
        """
        return [data.to_grid_format() for data in data_list]
    
    @staticmethod
    def generate_batch_id() -> str:
        """
        生成上传批次ID
        格式: UPLOAD_YYYYMMDD_HHMMSS_RANDOM
        
        返回:
            批次ID字符串
        """
        from datetime import datetime
        import random
        import string
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"UPLOAD_{timestamp}_{random_str}"
    
    @staticmethod
    def update_data_status(data_list: List[GridData], status: str, response: str = None):
        """
        更新数据状态
        
        参数:
            data_list: GridData对象列表
            status: 新状态
            response: 上传响应信息
        """
        for data in data_list:
            data.status = status
            if response:
                data.upload_response = response
            if status == '已上传':
                data.upload_time = datetime.now()
        
        # 提交到数据库
        db.session.commit()
    
    @staticmethod
    def validate_data_range(start_time: Optional[datetime], end_time: Optional[datetime]) -> bool:
        """
        验证时间范围是否有效
        
        参数:
            start_time: 开始时间
            end_time: 结束时间
            
        返回:
            时间范围是否有效
        """
        if start_time and end_time and start_time > end_time:
            return False
        
        # 限制时间范围不超过30天
        if start_time and end_time and (end_time - start_time) > timedelta(days=30):
            return False
        
        return True
    
    @staticmethod
    def validate_limit(limit: int) -> int:
        """
        验证并调整数据条数限制
        
        参数:
            limit: 请求的数据条数
            
        返回:
            调整后的数据条数
        """
        if limit is None:
            return Config.DEFAULT_DATA_LIMIT
        
        # 确保不超过最大限制
        return min(limit, Config.MAX_DATA_LIMIT)