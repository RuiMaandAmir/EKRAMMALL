const request = require('../utils/request');

// 用户相关接口
const userApi = {
  // 用户注册
  register: (data) => {
    return request.post('/accounts/register/', data);
  },
  
  // 用户登录
  login: (data) => {
    return request.post('/accounts/login/', data);
  },
  
  // 用户退出登录
  logout: () => {
    return request.post('/accounts/logout/');
  },
  
  // 获取用户信息
  getProfile: () => {
    return request.get('/accounts/profile/');
  },
  
  // 更新用户信息
  updateProfile: (data) => {
    return request.put('/accounts/profile/', data);
  },
  
  // 修改密码
  changePassword: (data) => {
    return request.post('/accounts/change-password/', data);
  },
  
  // 微信登录
  wechatAuth: (code) => {
    return request.post('/accounts/wechat-auth/', { code });
  }
};

// 分销商相关接口
const distributorApi = {
  // 成为分销商
  becomeDistributor: (data) => {
    return request.post('/accounts/become-distributor/', data);
  },
  
  // 获取分销商仪表盘数据
  getDashboard: () => {
    return request.get('/accounts/distributor-dashboard/');
  },
  
  // 获取团队成员
  getTeam: () => {
    return request.get('/accounts/distributor-team/');
  },
  
  // 申请提现
  applyWithdrawal: (data) => {
    return request.post('/accounts/apply-withdrawal/', data);
  },
  
  // 获取佣金记录
  getCommissions: () => {
    return request.get('/accounts/commissions/');
  },
  
  // 获取提现记录
  getWithdrawals: () => {
    return request.get('/accounts/withdrawals/');
  }
};

// 产品相关接口
const productApi = {
  // 获取产品列表
  getProducts: (params) => {
    return request.get('/products/products/', params);
  },
  
  // 获取产品详情
  getProductDetail: (id) => {
    return request.get(`/products/products/${id}/`);
  },
  
  // 获取推荐产品
  getFeaturedProducts: () => {
    return request.get('/products/featured/');
  },
  
  // 获取分类列表
  getCategories: () => {
    return request.get('/products/categories/');
  },
  
  // 获取分类下的产品
  getCategoryProducts: (categoryId, params) => {
    return request.get(`/products/category/${categoryId}/`, params);
  },
  
  // 搜索产品
  searchProducts: (keyword) => {
    return request.get('/products/search/', { keyword });
  },
  
  // 生成分销链接
  generateDistributionLink: (productId) => {
    return request.post(`/products/generate-distribution-link/${productId}/`);
  },
  
  // 通过分销码获取产品
  getProductByDistributionCode: (code) => {
    return request.get(`/products/by-distribution-code/${code}/`);
  }
};

// 购物车相关接口
const cartApi = {
  // 获取购物车详情
  getCart: () => {
    return request.get('/orders/cart/');
  },
  
  // 添加商品到购物车
  addToCart: (data) => {
    return request.post('/orders/cart/add/', data);
  },
  
  // 更新购物车商品数量
  updateCartItem: (itemId, data) => {
    return request.put(`/orders/cart/update/${itemId}/`, data);
  },
  
  // 从购物车移除商品
  removeFromCart: (itemId) => {
    return request.delete(`/orders/cart/remove/${itemId}/`);
  },
  
  // 清空购物车
  clearCart: () => {
    return request.post('/orders/cart/clear/');
  },
  
  // 应用分销码
  applyDistributorCode: (code) => {
    return request.post('/orders/cart/apply-distributor-code/', { code });
  }
};

// 订单相关接口
const orderApi = {
  // 结算
  checkout: (data) => {
    return request.post('/orders/checkout/', data);
  },
  
  // 获取我的订单
  getMyOrders: (params) => {
    return request.get('/orders/orders/my/', params);
  },
  
  // 获取订单详情
  getOrderDetail: (orderNumber) => {
    return request.get(`/orders/orders/${orderNumber}/`);
  },
  
  // 支付订单
  payOrder: (orderNumber, data) => {
    return request.post(`/orders/orders/${orderNumber}/pay/`, data);
  },
  
  // 取消订单
  cancelOrder: (orderNumber) => {
    return request.post(`/orders/orders/${orderNumber}/cancel/`);
  }
};

// 促销相关接口
const promotionApi = {
  // 获取轮播图
  getBanners: () => {
    return request.get('/promotions/banners/');
  },
  
  // 获取弹窗
  getPopups: () => {
    return request.get('/promotions/popups/');
  },
  
  // 获取活动页
  getActivities: () => {
    return request.get('/promotions/activities/');
  },
  
  // 获取用户优惠券
  getUserCoupons: () => {
    return request.get('/promotions/user-coupons/');
  },
  
  // 领取优惠券
  claimCoupon: (couponId) => {
    return request.post(`/promotions/user-coupons/${couponId}/claim/`);
  },
  
  // 获取正在进行的限时抢购活动
  getActiveFlashes: () => {
    return request.get('/promotions/active-flashes/');
  },
  
  // 获取限时抢购活动的商品
  getFlashProducts: (flashId) => {
    return request.get(`/promotions/flash-products/${flashId}/`);
  }
};

// 数据分析相关接口
const dashboardApi = {
  // 记录用户活动
  recordActivity: (data) => {
    return request.post('/dashboard/record-activity/', data);
  }
};

module.exports = {
  userApi,
  distributorApi,
  productApi,
  cartApi,
  orderApi,
  promotionApi,
  dashboardApi
}; 