import request from '@/utils/request'

// 优惠券相关接口
export function getCoupons(params) {
  return request({
    url: '/api/coupons/',
    method: 'get',
    params
  })
}

export function createCoupon(data) {
  return request({
    url: '/api/coupons/',
    method: 'post',
    data
  })
}

export function updateCoupon(id, data) {
  return request({
    url: `/api/coupons/${id}/`,
    method: 'put',
    data
  })
}

export function deleteCoupon(id) {
  return request({
    url: `/api/coupons/${id}/`,
    method: 'delete'
  })
}

export function useCoupon(id, data) {
  return request({
    url: `/api/coupons/${id}/use/`,
    method: 'post',
    data
  })
}

// 活动相关接口
export function getActivities(params) {
  return request({
    url: '/api/promotion-activities/',
    method: 'get',
    params
  })
}

export function createActivity(data) {
  return request({
    url: '/api/promotion-activities/',
    method: 'post',
    data
  })
}

export function updateActivity(id, data) {
  return request({
    url: `/api/promotion-activities/${id}/`,
    method: 'put',
    data
  })
}

export function deleteActivity(id) {
  return request({
    url: `/api/promotion-activities/${id}/`,
    method: 'delete'
  })
}

// 活动商品相关接口
export function getActivityProducts(activityId) {
  return request({
    url: `/api/promotion-activities/${activityId}/products/`,
    method: 'get'
  })
}

export function addActivityProduct(activityId, data) {
  return request({
    url: `/api/promotion-activities/${activityId}/add_product/`,
    method: 'post',
    data
  })
}

export function updateActivityProduct(activityId, productId, data) {
  return request({
    url: `/api/promotion-activities/${activityId}/update_product/`,
    method: 'post',
    data: {
      product_id: productId,
      ...data
    }
  })
}

export function removeActivityProduct(activityId, productId) {
  return request({
    url: `/api/promotion-activities/${activityId}/remove_product/`,
    method: 'post',
    data: {
      product_id: productId
    }
  })
}

// 商品相关接口
export function getAvailableProducts() {
  return request({
    url: '/api/products/available/',
    method: 'get'
  })
}

// 统计数据接口
export function getPromotionStats() {
  return request({
    url: '/api/promotion-stats/',
    method: 'get'
  })
}

export function getCouponStats() {
  return request({
    url: '/api/coupon-stats/',
    method: 'get'
  })
}

export function getActivityStats() {
  return request({
    url: '/api/activity-stats/',
    method: 'get'
  })
}

// 导出促销统计数据
export function exportPromotionStats(params) {
  return request({
    url: '/api/promotion/export/',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 导出促销数据
export function exportPromotionData(params) {
  return request({
    url: '/api/promotions/export/',
    method: 'get',
    params,
    responseType: 'blob'
  })
}