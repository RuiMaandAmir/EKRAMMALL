/**
 * 请求封装
 */
const app = getApp();

const BASE_URL = 'http://localhost:8000/api'

/**
 * 请求拦截器
 */
const requestInterceptor = (config) => {
  const token = wx.getStorageSync('token')
  if (token) {
    config.header = {
      ...config.header,
      'Authorization': `Bearer ${token}`
    }
  }
  return config
}

/**
 * 响应拦截器
 */
const responseInterceptor = (response) => {
  if (response.statusCode === 401) {
    // token过期，清除本地存储并跳转到登录页
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    wx.navigateTo({
      url: '/pages/auth/index'
    })
    return Promise.reject(new Error('未授权'))
  }
  return response.data
}

/**
 * 错误处理
 */
const errorHandler = (error) => {
  wx.showToast({
    title: error.message || '请求失败',
    icon: 'none',
    duration: 2000
  })
  return Promise.reject(error)
}

/**
 * 基础请求方法
 */
const request = (options) => {
  const { url, method = 'GET', data, header = {} } = options
  
  // 应用请求拦截器
  const config = requestInterceptor({
    url: `${BASE_URL}${url}`,
    method,
    data,
    header
  })

  return new Promise((resolve, reject) => {
    wx.request({
      ...config,
      success: (res) => {
        try {
          const response = responseInterceptor(res)
          resolve(response)
        } catch (error) {
          reject(error)
        }
      },
      fail: (error) => {
        errorHandler(error)
        reject(error)
      }
    })
  })
}

/**
 * GET请求
 */
const get = (url, data, header) => {
  return request({ url, method: 'GET', data, header })
}

/**
 * POST请求
 */
const post = (url, data, header) => {
  return request({ url, method: 'POST', data, header })
}

/**
 * PUT请求
 */
const put = (url, data, header) => {
  return request({ url, method: 'PUT', data, header })
}

/**
 * DELETE请求
 */
const del = (url, data, header) => {
  return request({ url, method: 'DELETE', data, header })
}

/**
 * 上传文件
 */
function upload(url, filePath, name = 'file', formData = {}, options = {}) {
  const baseUrl = app ? app.globalData.apiUrl : 'http://localhost:8000/api';
  const token = wx.getStorageSync('token');
  
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: baseUrl + url,
      filePath,
      name,
      formData,
      header: {
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        let data = res.data;
        try {
          data = JSON.parse(data);
        } catch (e) {
          // 不是JSON格式
        }
        if (res.statusCode === 200) {
          resolve(data);
        } else {
          reject(data);
          wx.showToast({
            title: data.message || '上传失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        reject(err);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none',
          duration: 2000
        });
      }
    });
  });
}

export default {
  get,
  post,
  put,
  delete: del,
  upload
}; 