import unittest
import requests
import time
import threading
from app import app, db
from models import GridData
from datetime import datetime, timedelta
import traceback
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GridAPITest(unittest.TestCase):
    BASE_URL = "http://localhost:5000"
    
    @classmethod
    def setUpClass(cls):
        """在测试类开始前启动 Flask 服务器"""
        print("启动 Flask 服务器...")
        
        # 创建并启动服务器线程
        cls.server_thread = threading.Thread(target=cls.run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # 等待服务器启动
        cls.wait_for_server()
        
        # 初始化数据库
        with app.app_context():
            db.create_all()
            cls.add_test_data()
    
    @classmethod
    def run_server(cls):
        """运行 Flask 服务器"""
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
    @classmethod
    def wait_for_server(cls):
        """等待服务器启动"""
        print("等待服务器启动...")
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.BASE_URL}/", timeout=1, verify=False)
                if response.status_code == 200:
                    print("服务器已启动")
                    return
            except:
                pass
            
            print(f"等待服务器启动 ({i+1}/{max_retries})...")
            time.sleep(1)
        
        raise RuntimeError("无法启动服务器或连接到服务器")
    
    @classmethod
    def add_test_data(cls):
        """添加测试数据"""
        print("添加测试数据...")
        with app.app_context():
            try:
                # 清空现有数据
                db.session.query(GridData).delete()
                db.session.commit()
                print("已清空现有数据")
            except Exception as e:
                print(f"清空数据时出错: {str(e)}")
                db.session.rollback()
            
            # 添加测试数据
            test_data = [
                GridData(
                    timestamp=datetime.now() - timedelta(days=5),
                    data_type='voltage',
                    value=220.5,
                    unit='kV',
                    device_id='device_001',
                    status='未上传'
                ),
                GridData(
                    timestamp=datetime.now() - timedelta(days=4),
                    data_type='current',
                    value=1200.3,
                    unit='A',
                    device_id='device_001',
                    status='未上传'
                ),
                GridData(
                    timestamp=datetime.now() - timedelta(days=3),
                    data_type='voltage',
                    value=219.8,
                    unit='kV',
                    device_id='device_002',
                    status='未上传'
                ),
                GridData(
                    timestamp=datetime.now() - timedelta(days=2),
                    data_type='current',
                    value=1180.7,
                    unit='A',
                    device_id='device_002',
                    status='未上传'
                ),
                GridData(
                    timestamp=datetime.now() - timedelta(days=1),
                    data_type='voltage',
                    value=221.2,
                    unit='kV',
                    device_id='device_003',
                    status='未上传'
                )
            ]
            
            try:
                db.session.add_all(test_data)
                db.session.commit()
                print(f"成功添加 {len(test_data)} 条测试数据")
                
                # 验证数据是否添加成功
                count = GridData.query.count()
                print(f"当前数据库中有 {count} 条记录")
            except Exception as e:
                print(f"添加测试数据时出错: {str(e)}")
                db.session.rollback()
    
    def test_upload_with_time_range(self):
        """测试按时间范围上传数据"""
        test_data = {
            "start_time": (datetime.now() - timedelta(days=5)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "limit": 3
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/grid/data/upload",
            json=test_data,
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data_count'], 3)
    
    def test_upload_with_device_ids(self):
        """测试按设备ID上传数据"""
        test_data = {
            "device_ids": ["device_001"],
            "limit": 2
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/grid/data/upload",
            json=test_data,
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data_count'], 2)
    
    def test_upload_with_data_types(self):
        """测试按数据类型上传数据"""
        test_data = {
            "data_types": ["voltage"],
            "limit": 2
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/grid/data/upload",
            json=test_data,
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data_count'], 2)
    
    def test_upload_no_data(self):
        """测试无数据情况"""
        test_data = {
            "start_time": "2020-01-01T00:00:00",
            "end_time": "2020-01-02T00:00:00"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/grid/data/upload",
            json=test_data,
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data_count'], 0)
        self.assertEqual(data['message'], '没有符合条件的数据')
    
    def test_invalid_time_range(self):
        """测试无效时间范围"""
        test_data = {
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() - timedelta(days=1)).isoformat()
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/grid/data/upload",
            json=test_data,
            verify=False
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], '无效的时间范围')
    
    def test_exceed_max_limit(self):
        """测试超过最大数据条数限制"""
        test_data = {
            "limit": 1500
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/grid/data/upload",
            json=test_data,
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        # 应限制为MAX_DATA_LIMIT
        self.assertEqual(data['data_count'], 1000)  # MAX_DATA_LIMIT
    
    def test_get_upload_status(self):
        """测试获取上传状态"""
        response = requests.get(
            f"{self.BASE_URL}/api/grid/data/status",
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
    
    def test_get_data_count(self):
        """测试获取数据统计"""
        response = requests.get(
            f"{self.BASE_URL}/api/grid/data/count?status=未上传",
            verify=False
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 5)  # 我们添加了5条测试数据
    
    @classmethod
    def tearDownClass(cls):
        """测试结束后清理数据库"""
        print("清理测试数据...")
        with app.app_context():
            db.drop_all()

if __name__ == '__main__':
    unittest.main()