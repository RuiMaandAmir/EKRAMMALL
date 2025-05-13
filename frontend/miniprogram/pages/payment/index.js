const app = getApp()

Page({
  data: {
    order: null,
    paymentMethod: 'wechat'
  },
  
  onLoad(options) {
    const { order_number } = options
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
        } else {
          wx.showToast({
            title: '获取订单信息失败',
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
  
  selectPaymentMethod(e) {
    const method = e.currentTarget.dataset.method
    this.setData({
      paymentMethod: method
    })
  },
  
  handlePay() {
    if (!this.data.order) {
      wx.showToast({
        title: '订单信息不完整',
        icon: 'none'
      })
      return
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/orders/${this.data.order.order_number}/pay/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const payData = res.data
          // 调用微信支付
          wx.requestPayment({
            ...payData,
            success: () => {
              // 支付成功，跳转到支付结果页面
              wx.redirectTo({
                url: `/pages/payment/result/index?order_number=${this.data.order.order_number}&status=success`
              })
            },
            fail: (err) => {
              if (err.errMsg !== 'requestPayment:fail cancel') {
                wx.redirectTo({
                  url: `/pages/payment/result/index?order_number=${this.data.order.order_number}&status=fail`
                })
              }
            }
          })
        } else {
          wx.showToast({
            title: '创建支付订单失败',
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
  }
}) 