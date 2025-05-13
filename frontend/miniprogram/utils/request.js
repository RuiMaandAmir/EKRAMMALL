/**
 * 请求封装
 */
const app = getApp();

/**
 * 请求拦截器
 */
function requestInterceptor(config) {
  const token = wx.getStorageSync('token');
  if (token) {
    config.header = {
      ...config.header,
      'Authorization': `Bearer ${token}`
    };
  }
  return config;
}

/**
 * 响应拦截器
 */
function responseInterceptor(response) {
  // 请求成功但业务状态码错误
  if (response.statusCode !== 200) {
    // 401 未授权，跳转登录页
    if (response.statusCode === 401) {
      wx.removeStorageSync('token');
      wx.removeStorageSync('userInfo');
      app.globalData.isLoggedIn = false;
      
      wx.showToast({
        title: '登录已过期，请重新登录',
        icon: 'none',
        duration: 2000
      });
      
      setTimeout(() => {
        wx.navigateTo({
          url: '/pages/auth/login',
        });
      }, 1000);
    } else {
      wx.showToast({
        title: response.data.message || '请求失败',
        icon: 'none',
        duration: 2000
      });
    }
    return Promise.reject(response);
  }
  return response.data;
}

/**
 * 基础请求方法
 */
function request(options) {
  const baseUrl = app ? app.globalData.apiUrl : 'http://localhost:8000/api';
  
  // 拦截器处理
  const config = requestInterceptor({
    url: baseUrl + options.url,
    method: options.method || 'GET',
    data: options.data,
    header: {
      'Content-Type': 'application/json',
      ...options.header
    }
  });
  
  return new Promise((resolve, reject) => {
    wx.request({
      ...config,
      success: (res) => {
        try {
          const response = responseInterceptor(res);
          resolve(response);
        } catch (error) {
          reject(error);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none',
          duration: 2000
        });
        reject(err);
      }
    });
  });
}

/**
 * GET请求
 */
function get(url, data = {}, options = {}) {
  return request({
    url,
    method: 'GET',
    data,
    ...options
  });
}

/**
 * POST请求
 */
function post(url, data = {}, options = {}) {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  });
}

/**
 * PUT请求
 */
function put(url, data = {}, options = {}) {
  return request({
    url,
    method: 'PUT',
    data,
    ...options
  });
}

/**
 * DELETE请求
 */
function del(url, data = {}, options = {}) {
  return request({
    url,
    method: 'DELETE',
    data,
    ...options
  });
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

module.exports = {
  request,
  get,
  post,
  put,
  delete: del,
  upload
}; 