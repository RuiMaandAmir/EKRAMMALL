import request from '@/utils/request';

/**
 * 获取广告列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getAdList(params) {
  return request({
    url: '/ads',
    method: 'get',
    params
  });
}

/**
 * 创建广告
 * @param {Object} data - 广告数据
 * @returns {Promise}
 */
export function createAd(data) {
  return request({
    url: '/ads',
    method: 'post',
    data
  });
}

/**
 * 更新广告
 * @param {number|string} id - 广告ID
 * @param {Object} data - 广告数据
 * @returns {Promise}
 */
export function updateAd(id, data) {
  return request({
    url: `/ads/${id}`,
    method: 'put',
    data
  });
}

/**
 * 删除广告
 * @param {number|string} id - 广告ID
 * @returns {Promise}
 */
export function deleteAd(id) {
  return request({
    url: `/ads/${id}`,
    method: 'delete'
  });
}

/**
 * 获取广告详情
 * @param {number|string} id - 广告ID
 * @returns {Promise}
 */
export function getAdDetail(id) {
  return request({
    url: `/ads/${id}`,
    method: 'get'
  });
} 