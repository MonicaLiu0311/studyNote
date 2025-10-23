from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class GridData(db.Model):
    """
    电网数据模型
    存储需要上传到国网平台的数据
    """
    __tablename__ = 'grid_data'
    
    # 主键ID
    id = db.Column(db.Integer, primary_key=True)
    
    # 数据时间戳
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    
    # 数据类型
    data_type = db.Column(db.String(50), nullable=False, index=True)
    
    # 数据值
    value = db.Column(db.Float, nullable=False)
    
    # 数据单位
    unit = db.Column(db.String(20), nullable=False)
    
    # 设备ID
    device_id = db.Column(db.String(50), nullable=False, index=True)
    
    # 变电站/线路信息
    substation = db.Column(db.String(100))
    line = db.Column(db.String(100))
    
    # 数据质量标志
    quality = db.Column(db.String(20), default='正常')
    
    # 数据状态（是否已上传）
    status = db.Column(db.String(20), default='未上传', index=True)
    
    # 上传时间
    upload_time = db.Column(db.DateTime)
    
    # 上传响应
    upload_response = db.Column(db.Text)
    
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于JSON序列化
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'data_type': self.data_type,
            'value': self.value,
            'unit': self.unit,
            'device_id': self.device_id,
            'substation': self.substation,
            'line': self.line,
            'quality': self.quality,
            'status': self.status,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_grid_format(self):
        """
        转换为国网平台要求的数据格式
        根据国网平台API文档调整此方法
        """
        return {
            'dataId': self.id,
            'dataTime': self.timestamp.isoformat() if self.timestamp else None,
            'dataType': self.data_type,
            'dataValue': self.value,
            'dataUnit': self.unit,
            'deviceId': self.device_id,
            'substationName': self.substation,
            'lineName': self.line,
            'qualityFlag': self.quality,
            'createTime': self.created_at.isoformat() if self.created_at else None
        }

class UploadLog(db.Model):
    """
    数据上传日志模型
    记录每次数据上传的情况
    """
    __tablename__ = 'upload_logs'
    
    # 主键ID
    id = db.Column(db.Integer, primary_key=True)
    
    # 上传批次ID
    batch_id = db.Column(db.String(50), nullable=False, index=True)
    
    # 上传时间
    upload_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # 上传数据条数
    data_count = db.Column(db.Integer, nullable=False)
    
    # 上传状态
    status = db.Column(db.String(20), nullable=False)  # 成功/失败/部分成功
    
    # 成功条数
    success_count = db.Column(db.Integer, default=0)
    
    # 失败条数
    fail_count = db.Column(db.Integer, default=0)
    
    # 错误信息
    error_message = db.Column(db.Text)
    
    # 响应内容
    response = db.Column(db.Text)
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        """
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'data_count': self.data_count,
            'status': self.status,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'error_message': self.error_message
        }