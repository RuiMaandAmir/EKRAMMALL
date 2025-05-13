import request from '@/utils/request';

/**
 * 获取产品列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getProducts(params) {
  return request({
    url: '/api/products/',
    method: 'get',
    params
  });
}

/**
 * 获取产品详情
 * @param {number|string} id - 产品ID
 * @returns {Promise}
 */
export function getProduct(id) {
  return request({
    url: `/api/products/${id}/`,
    method: 'get'
  });
}

/**
 * 创建产品
 * @param {Object} data - 产品数据
 * @returns {Promise}
 */
export function createProduct(data) {
  return request({
    url: '/api/products/',
    method: 'post',
    data
  });
}

/**
 * 更新产品
 * @param {number|string} id - 产品ID
 * @param {Object} data - 产品数据
 * @returns {Promise}
 */
export function updateProduct(id, data) {
  return request({
    url: `/api/products/${id}/`,
    method: 'put',
    data
  });
}

/**
 * 删除产品
 * @param {number|string} id - 产品ID
 * @returns {Promise}
 */
export function deleteProduct(id) {
  return request({
    url: `/api/products/${id}/`,
    method: 'delete'
  });
}

/**
 * 获取产品分类列表
 * @returns {Promise}
 */
export function getCategories() {
  return request({
    url: '/api/categories/',
    method: 'get'
  });
}

/**
 * 获取产品库存
 * @param {number|string} id - 产品ID
 * @returns {Promise}
 */
export function getProductStock(id) {
  return request({
    url: `/api/products/${id}/stock/`,
    method: 'get'
  });
}

/**
 * 更新产品库存
 * @param {number|string} id - 产品ID
 * @param {Object} data - 产品库存数据
 * @returns {Promise}
 */
export function updateProductStock(id, data) {
  return request({
    url: `/api/products/${id}/stock/`,
    method: 'put',
    data
  });
}

/**
 * 获取产品销售统计
 * @param {number|string} id - 产品ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getProductSales(id, params) {
  return request({
    url: `/api/products/${id}/sales/`,
    method: 'get',
    params
  });
}

/**
 * 上架/下架产品
 * @param {number|string} id - 产品ID
 * @param {boolean} status - 上架状态
 * @returns {Promise}
 */
export function updateProductStatus(id, status) {
  return request({
    url: `/products/${id}/status/`,
    method: 'put',
    data: { status }
  });
}

/**
 * 批量删除产品
 * @param {Array} ids - 产品ID数组
 * @returns {Promise}
 */
export function batchDeleteProducts(ids) {
  return request({
    url: '/products/batch/',
    method: 'delete',
    data: { ids }
  });
} 