const app = getApp()

Page({
  data: {
    order: null,
    logistics: null
  },

  onLoad(options) {
    const { order_number } = options
    if (order_number) {
      this.getOrderDetail(order_number)
      this.getLogisticsInfo(order_number)
    }
  },

  getOrderDetail(order_number) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/orders/${order_number}/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            order: res.data
          })
        }
      }
    })
  },

  getLogisticsInfo(order_number) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/orders/${order_number}/logistics/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            logistics: res.data
          })
        } else {
          wx.showToast({
            title: '获取物流信息失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  copyTrackingNumber() {
    const { logistics } = this.data
    if (logistics && logistics.tracking_number) {
      wx.setClipboardData({
        data: logistics.tracking_number,
        success: () => {
          wx.showToast({
            title: '复制成功',
            icon: 'success'
          })
        }
      })
    }
  }
}) 