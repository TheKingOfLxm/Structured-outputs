import os
from dotenv import load_dotenv
from app import create_app

# 加载 .env 文件
load_dotenv()

# 创建Flask应用
app = create_app(os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    # 开发环境运行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
