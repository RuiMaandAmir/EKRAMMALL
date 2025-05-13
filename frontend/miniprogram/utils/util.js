// 格式化时间
const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

// 格式化数字
const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

// 格式化金额
const formatPrice = price => {
  return parseFloat(price).toFixed(2)
}

// 格式化手机号
const formatPhone = phone => {
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 检查是否为空
const isEmpty = value => {
  return value === undefined || value === null || value === ''
}

// 深拷贝
const deepClone = obj => {
  if (obj === null || typeof obj !== 'object') return obj
  const clone = Array.isArray(obj) ? [] : {}
  for (let key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      clone[key] = deepClone(obj[key])
    }
  }
  return clone
}

// 防抖函数
const debounce = (fn, delay) => {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 节流函数
const throttle = (fn, delay) => {
  let timer = null
  let startTime = Date.now()
  return function (...args) {
    const curTime = Date.now()
    const remaining = delay - (curTime - startTime)
    if (timer) clearTimeout(timer)
    if (remaining <= 0) {
      fn.apply(this, args)
      startTime = Date.now()
    } else {
      timer = setTimeout(() => {
        fn.apply(this, args)
        startTime = Date.now()
      }, remaining)
    }
  }
}

// 获取当前页面路径
const getCurrentPageUrl = () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  return currentPage.route
}

// 获取当前页面参数
const getCurrentPageOptions = () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  return currentPage.options
}

// 检查是否登录
const checkLogin = () => {
  const token = wx.getStorageSync('token')
  if (!token) {
    wx.navigateTo({
      url: '/pages/auth/index'
    })
    return false
  }
  return true
}

// 显示加载提示
const showLoading = (title = '加载中') => {
  wx.showLoading({
    title,
    mask: true
  })
}

// 隐藏加载提示
const hideLoading = () => {
  wx.hideLoading()
}

// 显示成功提示
const showSuccess = (title = '成功', duration = 1500) => {
  wx.showToast({
    title,
    icon: 'success',
    duration
  })
}

// 显示失败提示
const showError = (title = '失败', duration = 1500) => {
  wx.showToast({
    title,
    icon: 'error',
    duration
  })
}

// 显示确认对话框
const showConfirm = (content, title = '提示') => {
  return new Promise((resolve, reject) => {
    wx.showModal({
      title,
      content,
      success: (res) => {
        if (res.confirm) {
          resolve(true)
        } else {
          resolve(false)
        }
      },
      fail: reject
    })
  })
}

export default {
  formatTime,
  formatNumber,
  formatPrice,
  formatPhone,
  isEmpty,
  deepClone,
  debounce,
  throttle,
  getCurrentPageUrl,
  getCurrentPageOptions,
  checkLogin,
  showLoading,
  hideLoading,
  showSuccess,
  showError,
  showConfirm
} 