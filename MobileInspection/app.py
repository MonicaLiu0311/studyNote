from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_  # 从核心SQLAlchemy导入
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from config import Config


# 创建Flask应用实例
app = Flask(__name__)

# 配置数据库连接URI
app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_mysql_uri()

# 禁用SQLAlchemy事件系统，提高性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化SQLAlchemy扩展
db = SQLAlchemy(app)

# 定义数据库模型

class CableInfo(db.Model):
    """
    线缆基本信息模型
    存储线缆的核心属性
    """
    __tablename__ = 'cable_info'  # 数据库表名
    
    # 表字段定义
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    cable_id = db.Column(db.String(50), unique=True, nullable=False)  # 线缆唯一ID
    specification = db.Column(db.String(100))  # 线缆规格型号
    production_date = db.Column(db.DateTime)  # 生产日期
    length = db.Column(db.Float)  # 线缆长度
    status = db.Column(db.String(20))  # 当前状态（合格/不合格）
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间

class ProcessRecord(db.Model):
    """
    工艺流程记录模型
    存储线缆生产过程中的各个工序信息
    """
    __tablename__ = 'process_records'  # 数据库表名
    
    # 表字段定义
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    cable_id = db.Column(db.String(50), db.ForeignKey('cable_info.cable_id'))  # 外键，关联线缆ID
    process_name = db.Column(db.String(50))  # 工序名称
    process_time = db.Column(db.DateTime)  # 工序完成时间
    operator_id = db.Column(db.String(20))  # 操作员ID
    machine_id = db.Column(db.String(20))  # 设备ID
    parameters = db.Column(db.JSON)  # 工序参数（JSON格式）
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间

class InspectionResult(db.Model):
    """
    检测结果模型
    存储线缆的质量检测数据
    """
    __tablename__ = 'inspection_results'  # 数据库表名
    
    # 表字段定义
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    cable_id = db.Column(db.String(50), db.ForeignKey('cable_info.cable_id'))  # 外键，关联线缆ID
    test_item = db.Column(db.String(50))  # 检测项目
    inspection_time = db.Column(db.DateTime)  # 检测时间
    test_value = db.Column(db.String(50))  # 检测值
    standard_value = db.Column(db.String(50))  # 标准值
    result = db.Column(db.String(20))  # 检测结果（合格/不合格）
    inspector_id = db.Column(db.String(20))  # 检测员ID
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间

class InventoryRecord(db.Model):
    """
    库存记录模型
    存储线缆的出入库信息
    """
    __tablename__ = 'inventory_records'  # 数据库表名
    
    # 表字段定义
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    cable_id = db.Column(db.String(50), db.ForeignKey('cable_info.cable_id'))  # 外键，关联线缆ID
    operation_type = db.Column(db.String(20))  # 操作类型（入库/出库）
    record_time = db.Column(db.DateTime)  # 记录时间
    location = db.Column(db.String(50))  # 库位
    operator_id = db.Column(db.String(20))  # 操作员ID
    notes = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间

class InspectionLog(db.Model):
    """
    巡检记录模型
    存储现场巡检的结果
    """
    __tablename__ = 'inspection_logs'  # 数据库表名
    
    # 表字段定义
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    cable_id = db.Column(db.String(50), db.ForeignKey('cable_info.cable_id'))  # 外键，关联线缆ID
    inspector_id = db.Column(db.String(20))  # 巡检员ID
    inspection_time = db.Column(db.DateTime, default=datetime.now)  # 巡检时间
    result = db.Column(db.String(20))  # 巡检结果（合格/不合格）
    notes = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间

# 定义API路由

@app.route('/cable')
def index():
    """
    首页路由
    渲染扫描页面
    """
    return render_template('index.html')

@app.route('/cable/<cable_id>')
def cable_detail(cable_id):
    """
    线缆详情页路由
    根据线缆ID渲染详情页面
    """
    return render_template('cable_info.html', cable_id=cable_id)

@app.route('/api/cable/<cable_id>', methods=['GET'])
def get_cable_data(cable_id):
    """
    获取线缆数据API
    返回指定线缆的所有相关信息
    """
    try:
        # 查询线缆基本信息
        cable_info = CableInfo.query.filter_by(cable_id=cable_id).first()
        if not cable_info:
            return jsonify({'error': 'Cable not found'}), 404
        
        # 查询关联数据
        processes = ProcessRecord.query.filter_by(cable_id=cable_id).order_by(ProcessRecord.process_time).all()
        inspections = InspectionResult.query.filter_by(cable_id=cable_id).order_by(InspectionResult.inspection_time).all()
        inventory = InventoryRecord.query.filter_by(cable_id=cable_id).order_by(InventoryRecord.record_time).all()
        inspection_logs = InspectionLog.query.filter_by(cable_id=cable_id).order_by(InspectionLog.inspection_time.desc()).all()
        
        # 将ORM对象转换为字典格式
        def model_to_dict(model):
            """将SQLAlchemy模型对象转换为字典"""
            return {column.name: getattr(model, column.name) for column in model.__table__.columns}
        
        # 构建响应数据
        return jsonify({
            'cable_info': model_to_dict(cable_info),
            'processes': [model_to_dict(p) for p in processes],
            'inspections': [model_to_dict(i) for i in inspections],
            'inventory': [model_to_dict(i) for i in inventory],
            'inspection_logs': [model_to_dict(l) for l in inspection_logs]
        })
    except Exception as e:
        # 异常处理
        return jsonify({'error': str(e)}), 500

@app.route('/api/qrcode/<cable_id>', methods=['GET'])
def generate_qrcode(cable_id):
    """
    生成二维码API
    为指定线缆生成二维码图片
    """
    try:
        # 验证线缆是否存在
        if not CableInfo.query.filter_by(cable_id=cable_id).first():
            return jsonify({'error': 'Cable not found'}), 404
        
        # 创建二维码实例
        qr = qrcode.QRCode(
            version=1,  # 二维码版本
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错级别
            box_size=10,  # 每个小格子的像素大小
            border=4,  # 边框大小
        )
        
        # 添加数据到二维码
        qr.add_data(f"{Config.QRCODE_BASE_URL}/{cable_id}")
        qr.make(fit=True)  # 自动调整大小
        
        # 生成二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 将图片转换为Base64编码
        buffered = BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # 返回结果
        return jsonify({
            'cable_id': cable_id,
            'qrcode': f"data:image/png;base64,{img_str}"  # 数据URI格式
        })
    except Exception as e:
        # 异常处理
        return jsonify({'error': str(e)}), 500

@app.route('/api/inspection', methods=['POST'])
def record_inspection():
    """
    记录巡检结果API - 修复重复提交问题
    """
    try:
        # 获取请求数据
        data = request.json
        print(f"收到巡检记录请求: {data}")
        
        # 验证必需字段
        required_fields = ['cable_id', 'inspector_id', 'result']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        cable_id = data['cable_id']
        inspector_id = data['inspector_id']
        result = data['result']
        notes = data.get('notes', '')
        
        # 严格的防重复提交检查：检查30秒内是否有完全相同的记录
        thirty_seconds_ago = datetime.now() - timedelta(seconds=30)
        
        existing_inspection = InspectionLog.query.filter(
            and_(
                InspectionLog.cable_id == cable_id,
                InspectionLog.inspector_id == inspector_id,
                InspectionLog.result == result,
                InspectionLog.notes == notes,
                InspectionLog.inspection_time >= thirty_seconds_ago
            )
        ).first()
        
        if existing_inspection:
            print(f"检测到重复提交，已存在记录ID: {existing_inspection.id}")
            return jsonify({'error': '请勿重复提交相同的巡检记录', 'existing_id': existing_inspection.id}), 400
        
        # 创建巡检记录对象
        inspection = InspectionLog(
            cable_id=cable_id,
            inspector_id=inspector_id,
            result=result,
            notes=notes
        )
        
        # 保存到数据库
        db.session.add(inspection)
        db.session.commit()
        
        print(f"巡检记录保存成功，ID: {inspection.id}")
        
        # 返回成功响应
        return jsonify({
            'status': 'success',
            'inspection_id': inspection.id,
            'message': '巡检记录提交成功'
        })
        
    except Exception as e:
        # 异常回滚
        db.session.rollback()
        print(f"巡检记录保存失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 应用入口
if __name__ == '__main__':
    # 启动开发服务器
    app.run(host='0.0.0.0', port=5000, debug=True)