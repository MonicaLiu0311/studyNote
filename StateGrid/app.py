import os
import time
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import traceback
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Config:
    """配置类"""
    # MySQL数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DB = os.getenv('MYSQL_DB', 'grid_data_db')
    
    # 国网平台API配置
    GRID_API_BASE_URL = os.getenv('GRID_API_BASE_URL', 'http://127.0.0.1:8000/grid')
    GRID_API_CLIENT_ID = os.getenv('GRID_API_CLIENT_ID', 'test_client_001')
    GRID_API_CLIENT_SECRET = os.getenv('GRID_API_CLIENT_SECRET', 'test_secret_123')
    GRID_API_TOKEN_URL = os.getenv('GRID_API_TOKEN_URL', '/oauth/token')
    GRID_API_DATA_URL = os.getenv('GRID_API_DATA_URL', '/api/v1/data/upload')
    
    # 数据限制配置
    DEFAULT_DATA_LIMIT = int(os.getenv('DEFAULT_DATA_LIMIT', 100))
    MAX_DATA_LIMIT = int(os.getenv('MAX_DATA_LIMIT', 1000))
    
    # 数据库URI
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# 存储访问令牌
tokens = {}

class GridData(db.Model):
    """电网数据模型"""
    __tablename__ = 'grid_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    data_type = db.Column(db.String(50), nullable=False, index=True)  # 数据类型：voltage, current, power等
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # 单位：kV, A, MW等
    device_id = db.Column(db.String(100), nullable=False, index=True)  # 设备ID
    status = db.Column(db.String(20), nullable=False, default='未上传')  # 状态：未上传、已上传、上传失败
    upload_time = db.Column(db.DateTime, nullable=True)  # 上传时间
    response_info = db.Column(db.Text, nullable=True)  # 上传响应信息
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'data_type': self.data_type,
            'value': self.value,
            'unit': self.unit,
            'device_id': self.device_id,
            'status': self.status,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UploadLog(db.Model):
    """上传日志模型"""
    __tablename__ = 'upload_log'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(50), nullable=False, unique=True, index=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    data_count = db.Column(db.Integer, nullable=False)
    success_count = db.Column(db.Integer, default=0)
    fail_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), nullable=False)  # 状态：成功、失败、部分成功
    error_message = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'data_count': self.data_count,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class DataProcessor:
    """数据处理类"""
    
    @staticmethod
    def validate_data_range(start_time: Optional[datetime], end_time: Optional[datetime]) -> bool:
        """验证时间范围"""
        if start_time and end_time:
            return start_time