import request from '../utils/request'

// 用户相关接口
export const userApi = {
  // 登录
  login: (data) => request.post('/auth/login/', data),
  // 注册
  register: (data) => request.post('/auth/register/', data),
  // 获取用户信息
  getUserInfo: () => request.get('/user/info/'),
  // 更新用户信息
  updateUserInfo: (data) => request.put('/user/info/', data),
  // 获取用户地址列表
  getAddressList: () => request.get('/user/address/'),
  // 添加地址
  addAddress: (data) => request.post('/user/address/', data),
  // 更新地址
  updateAddress: (id, data) => request.put(`/user/address/${id}/`, data),
  // 删除地址
  deleteAddress: (id) => request.delete(`/user/address/${id}/`)
}

// 商品相关接口
export const productApi = {
  // 获取商品列表
  getProducts: (params) => request.get('/products/', params),
  // 获取商品详情
  getProductDetail: (id) => request.get(`/products/${id}/`),
  // 获取商品分类
  getCategories: () => request.get('/categories/'),
  // 搜索商品
  searchProducts: (keyword) => request.get('/products/search/', { keyword })
}

// 购物车相关接口
export const cartApi = {
  // 获取购物车列表
  getCartList: () => request.get('/cart/'),
  // 添加商品到购物车
  addToCart: (data) => request.post('/cart/', data),
  // 更新购物车商品数量
  updateCartItem: (id, data) => request.put(`/cart/${id}/`, data),
  // 删除购物车商品
  removeCartItem: (id) => request.delete(`/cart/${id}/`),
  // 清空购物车
  clearCart: () => request.delete('/cart/clear/')
}

// 订单相关接口
export const orderApi = {
  // 创建订单
  createOrder: (data) => request.post('/orders/', data),
  // 获取订单列表
  getOrderList: (params) => request.get('/orders/', params),
  // 获取订单详情
  getOrderDetail: (id) => request.get(`/orders/${id}/`),
  // 取消订单
  cancelOrder: (id) => request.post(`/orders/${id}/cancel/`),
  // 确认收货
  confirmOrder: (id) => request.post(`/orders/${id}/confirm/`),
  // 删除订单
  deleteOrder: (id) => request.delete(`/orders/${id}/`)
}

// 支付相关接口
export const paymentApi = {
  // 创建支付订单
  createPayment: (orderId) => request.post('/payments/', { order_id: orderId }),
  // 查询支付状态
  queryPayment: (paymentId) => request.get(`/payments/${paymentId}/`),
  // 获取支付参数
  getPaymentParams: (paymentId) => request.get(`/payments/${paymentId}/params/`)
}

export default {
  user: userApi,
  product: productApi,
  cart: cartApi,
  order: orderApi,
  payment: paymentApi
} 