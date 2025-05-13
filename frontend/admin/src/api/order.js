import request from '@/utils/request';

/**
 * 获取订单列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getOrders(params) {
  return request({
    url: '/orders/',
    method: 'get',
    params
  });
}

/**
 * 获取订单详情
 * @param {number|string} id - 订单ID
 * @returns {Promise}
 */
export function getOrderDetail(id) {
  return request({
    url: `/orders/${id}/`,
    method: 'get'
  });
}

/**
 * 更新订单
 * @param {number|string} id - 订单ID
 * @param {Object} data - 订单数据
 * @returns {Promise}
 */
export function updateOrder(id, data) {
  return request({
    url: `/orders/${id}/`,
    method: 'put',
    data
  });
}

/**
 * 取消订单
 * @param {number|string} id - 订单ID
 * @param {string} reason - 取消原因
 * @returns {Promise}
 */
export function cancelOrder(id, reason) {
  return request({
    url: `/orders/${id}/cancel/`,
    method: 'post',
    data: { reason }
  });
}

/**
 * 确认订单
 * @param {number|string} id - 订单ID
 * @returns {Promise}
 */
export function confirmOrder(id) {
  return request({
    url: `/orders/${id}/confirm/`,
    method: 'post'
  });
}

/**
 * 发货
 * @param {number|string} id - 订单ID
 * @param {Object} data - 物流信息
 * @returns {Promise}
 */
export function shipOrder(id, data) {
  return request({
    url: `/orders/${id}/ship/`,
    method: 'post',
    data
  });
}

/**
 * 完成订单
 * @param {number|string} id - 订单ID
 * @returns {Promise}
 */
export function completeOrder(id) {
  return request({
    url: `/orders/${id}/complete/`,
    method: 'post'
  });
}

/**
 * 获取订单统计信息
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getOrderStatistics(params) {
  return request({
    url: '/orders/statistics/',
    method: 'get',
    params
  });
}

/**
 * 导出订单
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function exportOrders(params) {
  return request({
    url: '/orders/export/',
    method: 'get',
    params,
    responseType: 'blob'
  });
}

/**
 * 获取物流信息
 * @param {number|string} id - 订单ID
 * @returns {Promise}
 */
export function getShippingInfo(id) {
  return request({
    url: `/orders/${id}/shipping/`,
    method: 'get'
  });
} 