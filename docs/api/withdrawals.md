# 提现 API 文档

## 基础信息
- 基础路径: `/api/withdrawals/`
- 认证方式: Token认证
- 权限要求: 需要登录

## API 列表

### 1. 获取提现列表
- 请求方式: GET
- 路径: `/api/withdrawals/`
- 权限: 管理员可查看所有，普通用户只能查看自己的
- 参数:
  - `status`: 可选，按状态筛选
  - `start_date`: 可选，开始日期
  - `end_date`: 可选，结束日期
- 响应示例:
```json
{
    "count": 10,
    "results": [
        {
            "id": 1,
            "distributor": 1,
            "distributor_name": "张三",
            "amount": "100.00",
            "status": "pending",
            "bank_name": "中国银行",
            "bank_account": "6222********1234",
            "account_name": "张三",
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z"
        }
    ]
}
```

### 2. 创建提现申请
- 请求方式: POST
- 路径: `/api/withdrawals/`
- 权限: 分销商
- 请求体:
```json
{
    "amount": "100.00",
    "bank_name": "中国银行",
    "bank_account": "6222********1234",
    "account_name": "张三"
}
```
- 响应示例:
```json
{
    "id": 1,
    "status": "pending",
    "created_at": "2024-03-20T10:00:00Z"
}
```

### 3. 获取提现详情
- 请求方式: GET
- 路径: `/api/withdrawals/{id}/`
- 权限: 管理员或提现申请人
- 响应示例:
```json
{
    "id": 1,
    "distributor": 1,
    "distributor_name": "张三",
    "amount": "100.00",
    "status": "pending",
    "bank_name": "中国银行",
    "bank_account": "6222********1234",
    "account_name": "张三",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### 4. 通过提现申请
- 请求方式: POST
- 路径: `/api/withdrawals/{id}/approve/`
- 权限: 管理员
- 响应示例:
```json
{
    "status": "提现申请已通过"
}
```

### 5. 拒绝提现申请
- 请求方式: POST
- 路径: `/api/withdrawals/{id}/reject/`
- 权限: 管理员
- 请求体:
```json
{
    "remark": "银行信息不完整"
}
```
- 响应示例:
```json
{
    "status": "提现申请已拒绝"
}
```

### 6. 完成提现
- 请求方式: POST
- 路径: `/api/withdrawals/{id}/complete/`
- 权限: 管理员
- 响应示例:
```json
{
    "status": "提现已完成"
}
```

### 7. 获取提现统计
- 请求方式: GET
- 路径: `/api/withdrawals/statistics/`
- 权限: 管理员或分销商
- 响应示例:
```json
{
    "total_withdrawals": 10,
    "total_amount": "1000.00",
    "pending_count": 2,
    "approved_count": 3,
    "completed_count": 4,
    "rejected_count": 1,
    "available_balance": "500.00"
}
```

### 8. 获取提现状态汇总
- 请求方式: GET
- 路径: `/api/withdrawals/status_summary/`
- 权限: 管理员
- 响应示例:
```json
[
    {
        "status": "pending",
        "count": 2,
        "total_amount": "200.00"
    },
    {
        "status": "approved",
        "count": 3,
        "total_amount": "300.00"
    }
]
```

## 错误码说明
- 400: 请求参数错误
- 401: 未认证
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误 