# EKRAM商城后端

## 项目结构

```
backend/
├── ekram_mall/          # 项目配置目录
│   ├── settings.py      # 项目设置
│   ├── urls.py         # URL配置
│   └── wsgi.py         # WSGI配置
├── accounts/           # 用户账户应用
├── products/          # 商品管理应用
├── orders/           # 订单管理应用
├── promotions/       # 促销活动应用
├── dashboard/        # 数据统计应用
├── order_management/ # 订单处理应用
├── templates/        # 模板文件
│   └── admin/       # 管理后台模板
├── staticfiles/      # 静态文件
├── media/           # 上传文件
├── logs/            # 日志文件
├── requirements.txt  # 项目依赖
├── manage.py        # Django管理脚本
└── start_server.sh  # 服务启动脚本
```

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
复制 `.env.example` 到 `.env` 并修改配置

4. 初始化数据库：
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. 启动服务：
```bash
./start_server.sh
```

## 生产环境部署

1. 设置环境变量：
```bash
ENVIRONMENT=production
```

2. 配置 Nginx：
使用 `ekram_mall.conf` 配置文件

3. 启动服务：
```bash
./start_server.sh
```

## 目录说明

- `ekram_mall/`: 包含项目的核心配置文件
- `accounts/`: 用户账户管理，包括认证和授权
- `products/`: 商品管理，包括分类、品牌等
- `orders/`: 订单处理和管理
- `promotions/`: 促销活动和优惠券管理
- `dashboard/`: 数据统计和报表
- `order_management/`: 订单处理工作流
- `templates/admin/`: 自定义管理后台模板
- `staticfiles/`: 静态资源文件
- `media/`: 用户上传的文件
- `logs/`: 应用日志 