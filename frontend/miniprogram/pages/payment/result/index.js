const app = getApp()

Page({
  data: {
    status: '',
    order: null
  },
  
  onLoad(options) {
    const { order_number, status } = options
    this.setData({
      status
    })
    
    if (order_number) {
      this.getOrderDetail(order_number)
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
  
  viewOrder() {
    const { order } = this.data
    if (order) {
      wx.navigateTo({
        url: `/pages/order/detail/index?order_number=${order.order_number}`
      })
    }
  },
  
  backToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
}) 