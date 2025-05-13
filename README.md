# Ekram Mall

一个基于Django和Vue.js的电商平台系统。

## 功能特点

- 用户认证和授权
- 商品管理
- 订单管理
- 分销商系统
- 支付集成
- 后台管理界面

## 技术栈

### 后端
- Django
- Django REST framework
- PostgreSQL
- Redis

### 前端
- Vue.js
- Element UI
- Axios

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ekram_mall.git
cd ekram_mall
```

2. 安装后端依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息
```

5. 运行数据库迁移
```bash
cd backend
python manage.py migrate
```

6. 启动开发服务器
```bash
# 后端
cd backend
python manage.py runserver

# 前端
cd frontend
npm run dev
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

MIT License 