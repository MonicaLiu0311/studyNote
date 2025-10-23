import requests
import json
from typing import List, Dict, Any, Optional
from config import Config
from models import UploadLog, db
from datetime import datetime, timedelta

class GridAPIClient:
    """
    国网平台API客户端
    负责与国网平台进行认证和数据上传
    """
    
    def __init__(self):
        self.access_token = None
        self.token_expiry = None
    
    def authenticate(self) -> bool:
        """
        获取国网平台访问令牌
        
        返回:
            认证是否成功
        """
        try:
            # 准备认证数据
            auth_data = {
                'client_id': Config.GRID_API_CLIENT_ID,
                'client_secret': Config.GRID_API_CLIENT_SECRET,
                'grant_type': 'client_credentials'
            }
            
            # 发送认证请求
            auth_url = Config.get_grid_api_url(Config.GRID_API_TOKEN_URL)
            response = requests.post(
                auth_url,
                data=auth_data,
                timeout=30
            )
            
            # 检查响应
            if response.status_code == 200:
                auth_result = response.json()
                self.access_token = auth_result['access_token']
                # 计算令牌过期时间（提前5分钟刷新）
                self.token_expiry = datetime.now() + timedelta(seconds=auth_result['expires_in'] - 300)
                return True
            else:
                print(f"认证失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"认证过程中发生错误: {str(e)}")
            return False
    
    def check_token(self) -> bool:
        """
        检查访问令牌是否有效
        
        返回:
            令牌是否有效
        """
        # 如果没有令牌或已过期，重新认证
        if not self.access_token or datetime.now() >= self.token_expiry:
            return self.authenticate()
        return True
    
    def upload_data(self, data: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
        """
        上传数据到国网平台
        
        参数:
            data: 要上传的数据列表
            batch_id: 上传批次ID
            
        返回:
            上传结果
        """
        # 检查令牌
        if not self.check_token():
            return {'success': False, 'error': '认证失败'}
        
        try:
            # 准备请求头
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # 准备请求数据
            request_data = {
                'batch_id': batch_id,
                'data_count': len(data),
                'data': data
            }
            
            # 发送上传请求
            upload_url = Config.get_grid_api_url(Config.GRID_API_DATA_URL)
            response = requests.post(
                upload_url,
                headers=headers,
                data=json.dumps(request_data),
                timeout=60
            )
            
            # 解析响应
            if response.status_code == 200:
                result = response.json()
                return {'success': True, 'response': result}
            else:
                error_msg = f"上传失败: {response.status_code} - {response.text}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"上传过程中发生错误: {str(e)}"
            return {'success': False, 'error': error_msg}
    
    def log_upload(
        self,
        batch_id: str,
        data_count: int,
        status: str,
        success_count: int = 0,
        fail_count: int = 0,
        error_message: str = None,
        response: str = None
    ):
        """
        记录上传日志
        
        参数:
            batch_id: 批次ID
            data_count: 数据条数
            status: 上传状态
            success_count: 成功条数
            fail_count: 失败条数
            error_message: 错误信息
            response: 响应内容
        """
        try:
            # 创建上传日志记录
            log = UploadLog(
                batch_id=batch_id,
                data_count=data_count,
                status=status,
                success_count=success_count,
                fail_count=fail_count,
                error_message=error_message,
                response=response
            )
            
            # 保存到数据库
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            print(f"记录上传日志失败: {str(e)}")
            db.session.rollback()