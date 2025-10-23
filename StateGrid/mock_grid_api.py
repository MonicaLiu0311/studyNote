# 启动模拟国网平台API服务
from flask import Flask, request, jsonify
import ssl
import time

app = Flask(__name__)

# 模拟的认证信息（与配置一致）
CLIENT_ID = 'test_client_001'
CLIENT_SECRET = 'test_secret_123'

# 模拟的令牌存储
tokens = {}

@app.route('/grid/oauth/token', methods=['POST'])
def get_token():
    # 检查客户端凭证
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    grant_type = request.form.get('grant_type')
    
    if grant_type != 'client_credentials':
        return jsonify({'error': 'unsupported_grant_type'}), 400
    
    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        return jsonify({'error': 'invalid_client'}), 401
    
    # 生成模拟令牌
    access_token = f"mock_token_{int(time.time())}"
    expires_in = 3600  # 1小时
    tokens[access_token] = time.time() + expires_in
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': expires_in
    })

@app.route('/grid/api/v1/data/upload', methods=['POST'])
def upload_data():
    # 检查认证头
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'unauthorized'}), 401
    
    token = auth_header.split(' ')[1]
    if token not in tokens or tokens[token] < time.time():
        return jsonify({'error': 'invalid_token'}), 401
    
    # 获取上传的数据
    data = request.json
    print(f"收到上传数据: {data}")
    
    # 模拟处理
    return jsonify({
        'success': True,
        'message': '数据接收成功',
        'received_count': len(data.get('data', []))
    })

if __name__ == '__main__':
    # 创建自签名证书上下文
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')  # 需要生成自签名证书
    
    # 启动HTTPS服务
    app.run(host='0.0.0.0', port=5000, ssl_context=context)