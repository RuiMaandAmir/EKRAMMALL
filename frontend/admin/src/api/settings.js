import request from '@/utils/request';

/**
 * 获取系统设置
 * @returns {Promise} 返回请求的Promise对象
 */
export function getSystemSettings() {
  return request({
    url: '/api/settings',
    method: 'get'
  });
}

/**
 * 更新系统设置
 * @param {Object} data - 设置数据，包含type和data字段
 * @returns {Promise} 返回请求的Promise对象
 */
export function updateSystemSettings(data) {
  return request({
    url: '/api/settings',
    method: 'put',
    data
  });
}

/**
 * 获取物流公司列表
 * @returns {Promise} 返回请求的Promise对象
 */
export function getShippingCompanies() {
  return request({
    url: '/api/shipping/companies',
    method: 'get'
  });
}

/**
 * 获取支付方式列表
 * @returns {Promise} 返回请求的Promise对象
 */
export function getPaymentMethods() {
  return request({
    url: '/api/payment/methods',
    method: 'get'
  });
}

/**
 * 更新支付方式状态
 * @param {string} code - 支付方式代码
 * @param {boolean} enabled - 是否启用
 * @returns {Promise} 返回请求的Promise对象
 */
export function updatePaymentMethodStatus(code, enabled) {
  return request({
    url: `/api/payment/methods/${code}/status`,
    method: 'put',
    data: { enabled }
  });
}

/**
 * 测试短信发送
 * @param {Object} data - 测试数据
 * @returns {Promise} 返回请求的Promise对象
 */
export function testSms(data) {
  return request({
    url: '/api/settings/test-sms',
    method: 'post',
    data
  });
}

/**
 * 获取网站运行统计
 * @returns {Promise} 返回请求的Promise对象
 */
export function getSiteStats() {
  return request({
    url: '/api/settings/site-stats',
    method: 'get'
  });
}

/**
 * 清除系统缓存
 * @param {string} type - 缓存类型
 * @returns {Promise} 返回请求的Promise对象
 */
export function clearCache(type) {
  return request({
    url: '/api/settings/clear-cache',
    method: 'post',
    data: { type }
  });
}

/**
 * 备份数据库
 * @returns {Promise} 返回请求的Promise对象
 */
export function backupDatabase() {
  return request({
    url: '/api/settings/backup-database',
    method: 'post'
  });
}

/**
 * 获取备份列表
 * @returns {Promise} 返回请求的Promise对象
 */
export function getBackupList() {
  return request({
    url: '/api/settings/backups',
    method: 'get'
  });
}

/**
 * 恢复数据库
 * @param {string} filename - 备份文件名
 * @returns {Promise} 返回请求的Promise对象
 */
export function restoreDatabase(filename) {
  return request({
    url: '/api/settings/restore-database',
    method: 'post',
    data: { filename }
  });
}

/**
 * 删除备份
 * @param {string} filename - 备份文件名
 * @returns {Promise} 返回请求的Promise对象
 */
export function deleteBackup(filename) {
  return request({
    url: `/api/settings/backups/${filename}`,
    method: 'delete'
  });
} 