# run.py: 应用入口脚本

from app import create_app

# 创建应用实例并启动开发服务器
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) # 默认 host="0.0.0.0", port="5000"