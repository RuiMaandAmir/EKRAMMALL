import request from '@/utils/request';

// 用户登录
export function login(data) {
  return request({
    url: '/accounts/admin/login/',
    method: 'post',
    data
  });
}

// 获取用户信息
export function getInfo() {
  return request({
    url: '/accounts/admin/info/',
    method: 'get'
  });
}

// 用户退出登录
export function logout() {
  return request({
    url: '/accounts/admin/logout/',
    method: 'post'
  });
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/accounts/admin/change-password/',
    method: 'post',
    data
  });
}

// 更新个人信息
export function updateProfile(data) {
  return request({
    url: '/accounts/admin/profile/',
    method: 'put',
    data
  });
}

// 获取管理员列表
export function getAdminList(params) {
  return request({
    url: '/accounts/admins/',
    method: 'get',
    params
  });
}

// 创建管理员
export function createAdmin(data) {
  return request({
    url: '/accounts/admins/',
    method: 'post',
    data
  });
}

// 更新管理员
export function updateAdmin(id, data) {
  return request({
    url: `/accounts/admins/${id}/`,
    method: 'put',
    data
  });
}

// 删除管理员
export function deleteAdmin(id) {
  return request({
    url: `/accounts/admins/${id}/`,
    method: 'delete'
  });
}

// 重置密码
export function resetPassword(id) {
  return request({
    url: `/accounts/admins/${id}/reset-password/`,
    method: 'post'
  });
}

// 更新管理员状态
export function updateAdminStatus(id, status) {
  return request({
    url: `/accounts/admins/${id}/status/`,
    method: 'put',
    data: { status }
  });
}

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerList(params) {
  return request({
    url: '/api/customers',
    method: 'get',
    params
  });
}

/**
 * 获取用户详情
 * @param {number|string} id - 用户ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerDetail(id) {
  return request({
    url: `/api/customers/${id}`,
    method: 'get'
  });
}

/**
 * 更新用户信息
 * @param {number|string} id - 用户ID
 * @param {Object} data - 用户数据
 * @returns {Promise} 返回请求的Promise对象
 */
export function updateCustomer(id, data) {
  return request({
    url: `/api/customers/${id}`,
    method: 'put',
    data
  });
}

/**
 * 更新用户状态
 * @param {number|string} id - 用户ID
 * @param {boolean} status - 状态（true-启用，false-禁用）
 * @returns {Promise} 返回请求的Promise对象
 */
export function updateCustomerStatus(id, status) {
  return request({
    url: `/api/customers/${id}/status`,
    method: 'put',
    data: { status }
  });
}

/**
 * 获取用户订单
 * @param {number|string} id - 用户ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerOrders(id, params) {
  return request({
    url: `/api/customers/${id}/orders`,
    method: 'get',
    params
  });
}

/**
 * 获取用户地址
 * @param {number|string} id - 用户ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerAddresses(id) {
  return request({
    url: `/api/customers/${id}/addresses`,
    method: 'get'
  });
}

/**
 * 导出用户数据
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回请求的Promise对象
 */
export function exportCustomers(params) {
  return request({
    url: '/api/customers/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
}

/**
 * 获取用户消费统计
 * @param {number|string} id - 用户ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerSpendStats(id) {
  return request({
    url: `/api/customers/${id}/statistics`,
    method: 'get'
  });
}

/**
 * 添加用户备注
 * @param {number|string} id - 用户ID
 * @param {string} note - 备注内容
 * @returns {Promise} 返回请求的Promise对象
 */
export function addCustomerNote(id, note) {
  return request({
    url: `/api/customers/${id}/note`,
    method: 'post',
    data: { note }
  });
}

/**
 * 获取用户标签
 * @param {number|string} id - 用户ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerTags(id) {
  return request({
    url: `/api/customers/${id}/tags`,
    method: 'get'
  });
}

/**
 * 添加用户标签
 * @param {number|string} id - 用户ID
 * @param {Array} tags - 标签列表
 * @returns {Promise} 返回请求的Promise对象
 */
export function addCustomerTags(id, tags) {
  return request({
    url: `/api/customers/${id}/tags`,
    method: 'post',
    data: { tags }
  });
}

/**
 * 删除用户标签
 * @param {number|string} id - 用户ID
 * @param {string} tagId - 标签ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function removeCustomerTag(id, tagId) {
  return request({
    url: `/api/customers/${id}/tags/${tagId}`,
    method: 'delete'
  });
}

/**
 * 获取用户等级列表
 * @returns {Promise} 返回请求的Promise对象
 */
export function getCustomerLevels() {
  return request({
    url: '/api/customer-levels',
    method: 'get'
  });
}

/**
 * 更新用户等级
 * @param {number|string} id - 用户ID
 * @param {number|string} levelId - 等级ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function updateCustomerLevel(id, levelId) {
  return request({
    url: `/api/customers/${id}/level`,
    method: 'put',
    data: { level_id: levelId }
  });
} 