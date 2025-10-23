import logging
from datetime import datetime
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ApiLog
import json

logger = logging.getLogger('grid_api')

def validate_datetime(dt_str):
    """验证日期时间格式"""
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return None

def execute_raw_query(query, params=None):
    """执行原始SQL查询"""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def log_api_call(caller, status, start, end, count=0, error=None):
    """记录API调用日志"""
    try:
        duration = (end - start).total_seconds()
        ApiLog.objects.create(
            caller=caller,
            status=status,
            start_time=start,
            end_time=end,
            duration=duration,
            record_count=count,
            error_message=error[:255] if error else None
        )
    except Exception as e:
        logger.error(f"日志记录失败: {str(e)}")

class NationalGridUploadAPI(APIView):
    def get(self, request):
        """国网平台数据上传接口"""
        start_time = datetime.now()
        caller = request.META.get('REMOTE_ADDR', 'unknown')
        
        try:
            # 解析查询参数
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            limit = int(request.query_params.get('limit', 100))
            
            # 验证时间参数
            valid_start = validate_datetime(start_date) if start_date else None
            valid_end = validate_datetime(end_date) if end_date else None
            
            # 获取生产数据
            production_data = self.get_production_data(valid_start, valid_end, limit)
            
            # 获取工艺数据
            process_data = self.get_process_data(valid_start, valid_end, limit)
            
            # 构建响应
            response_data = {
                'status': 'success',
                'production_data': production_data,
                'process_data': process_data,
                'total_records': len(production_data) + len(process_data),
                'query_params': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'limit': limit
                }
            }
            
            # 记录成功日志
            log_api_call(
                caller=caller,
                status=ApiLog.SUCCESS,
                start=start_time,
                end=datetime.now(),
                count=len(production_data) + len(process_data)
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # 记录错误日志
            end_time = datetime.now()
            error_msg = f"接口错误: {str(e)}"
            logger.error(error_msg)
            log_api_call(
                caller=caller,
                status=ApiLog.FAILED,
                start=start_time,
                end=end_time,
                error=error_msg
            )
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_production_data(self, start_date, end_date, limit):
        """获取生产数据"""
        query = """
            SELECT id, product_code, product_name, specification, 
                   DATE_FORMAT(production_date, '%%Y-%%m-%%d %%H:%%i:%%s') AS production_date,
                   batch_number, quantity, operator, equipment_id, status,
                   DATE_FORMAT(create_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS create_time,
                   DATE_FORMAT(update_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS update_time
            FROM production_data
        """
        
        conditions = []
        params = []
        
        if start_date and end_date:
            conditions.append("production_date BETWEEN %s AND %s")
            params.extend([start_date, end_date])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY production_date DESC LIMIT %s"
        params.append(limit)
        
        return execute_raw_query(query, params)

    def get_process_data(self, start_date, end_date, limit):
        """获取工艺数据"""
        query = """
            SELECT id, process_code, process_name, process_version, parameters,
                   temperature, pressure, speed, operator,
                   DATE_FORMAT(execute_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS execute_time,
                   status,
                   DATE_FORMAT(create_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS create_time,
                   DATE_FORMAT(update_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS update_time
            FROM process_data
        """
        
        conditions = []
        params = []
        
        if start_date and end_date:
            conditions.append("execute_time BETWEEN %s AND %s")
            params.extend([start_date, end_date])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY execute_time DESC LIMIT %s"
        params.append(limit)
        
        return execute_raw_query(query, params)

# 测试视图
class TestAPIView(APIView):
    def get(self, request):
        """测试接口返回数据"""
        try:
            # 模拟不同查询条件
            test_cases = [
                {'limit': 5},
                {'start_date': '2023-01-01 00:00:00', 'end_date': '2023-12-31 23:59:59', 'limit': 10},
                {'start_date': 'invalid-date'}  # 错误日期测试
            ]
            
            results = []
            for case in test_cases:
                # 模拟请求对象
                class MockRequest:
                    query_params = case
                    META = {'REMOTE_ADDR': '127.0.0.1'}
                
                # 调用接口
                view = NationalGridUploadAPI()
                response = view.get(MockRequest())
                results.append({
                    'case': case,
                    'response': response.data,
                    'status': response.status_code
                })
            
            return Response({'test_results': results}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )