import request from '@/utils/request';

/**
 * 获取仪表盘数据概览
 * @returns {Promise}
 */
export function getDashboardSummary() {
  return request({
    url: '/statistics/dashboard/summary/',
    method: 'get'
  });
}

/**
 * 获取销售统计数据
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getSalesStatistics(params) {
  return request({
    url: '/statistics/sales/',
    method: 'get',
    params
  });
}

/**
 * 获取订单统计数据
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getOrderStatistics(params) {
  return request({
    url: '/statistics/orders/',
    method: 'get',
    params
  });
}

/**
 * 获取产品销量排行
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getProductRanking(params) {
  return request({
    url: '/statistics/products/ranking/',
    method: 'get',
    params
  });
}

/**
 * 获取用户统计数据
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getUserStatistics(params) {
  return request({
    url: '/statistics/users/',
    method: 'get',
    params
  });
}

/**
 * 获取新增用户数据
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getNewUserStatistics(params) {
  return request({
    url: '/statistics/users/new/',
    method: 'get',
    params
  });
}

/**
 * 获取用户地域分布
 * @returns {Promise}
 */
export function getUserRegions() {
  return request({
    url: '/statistics/users/regions/',
    method: 'get'
  });
}

/**
 * 获取销售趋势数据
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getSalesTrend(params) {
  return request({
    url: '/statistics/sales/trend/',
    method: 'get',
    params
  });
}

/**
 * 获取支付方式分布
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getPaymentMethodsStats(params) {
  return request({
    url: '/statistics/payments/methods/',
    method: 'get',
    params
  });
}

/**
 * 获取分类销售统计
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getCategoryStatistics(params) {
  return request({
    url: '/statistics/categories/',
    method: 'get',
    params
  });
}

/**
 * 导出统计报表
 * @param {string} type - 报表类型
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function exportStatisticsReport(type, params) {
  return request({
    url: `/statistics/export/${type}/`,
    method: 'get',
    params,
    responseType: 'blob'
  });
} 