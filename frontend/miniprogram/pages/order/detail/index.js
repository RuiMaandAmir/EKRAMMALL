const app = getApp()

Page({
  data: {
    order: null
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
            title: '获取订单详情失败',
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

  async cancelOrder() {
    try {
      const res = await wx.showModal({
        title: '提示',
        content: '确定要取消该订单吗？'
      })

      if (res.confirm) {
        await wx.request({
          url: `${app.globalData.baseUrl}/api/orders/${this.data.order.order_number}/cancel/`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${app.globalData.token}`
          }
        })

        wx.showToast({
          title: '取消成功',
          icon: 'success'
        })

        // 刷新订单详情
        this.getOrderDetail(this.data.order.order_number)
      }
    } catch (error) {
      console.error('取消订单失败:', error)
      wx.showToast({
        title: '取消失败',
        icon: 'none'
      })
    }
  },

  payOrder() {
    wx.navigateTo({
      url: `/pages/payment/index?order_number=${this.data.order.order_number}`
    })
  },

  async confirmReceive() {
    try {
      const res = await wx.showModal({
        title: '提示',
        content: '确认已收到商品？'
      })

      if (res.confirm) {
        await wx.request({
          url: `${app.globalData.baseUrl}/api/orders/${this.data.order.order_number}/confirm/`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${app.globalData.token}`
          }
        })

        wx.showToast({
          title: '确认成功',
          icon: 'success'
        })

        // 刷新订单详情
        this.getOrderDetail(this.data.order.order_number)
      }
    } catch (error) {
      console.error('确认收货失败:', error)
      wx.showToast({
        title: '确认失败',
        icon: 'none'
      })
    }
  },

  async deleteOrder() {
    try {
      const res = await wx.showModal({
        title: '提示',
        content: '确定要删除该订单吗？'
      })

      if (res.confirm) {
        await wx.request({
          url: `${app.globalData.baseUrl}/api/orders/${this.data.order.order_number}/`,
          method: 'DELETE',
          header: {
            'Authorization': `Bearer ${app.globalData.token}`
          }
        })

        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })

        // 返回上一页
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (error) {
      console.error('删除订单失败:', error)
      wx.showToast({
        title: '删除失败',
        icon: 'none'
      })
    }
  },

  viewLogistics() {
    wx.navigateTo({
      url: `/pages/order/logistics/index?order_number=${this.data.order.order_number}`
    })
  },

  buyAgain() {
    // 将商品添加到购物车
    const items = this.data.order.items
    items.forEach(item => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/cart/items/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: {
          product: item.product.id,
          variant: item.variant.id,
          quantity: item.quantity
        }
      })
    })

    wx.showToast({
      title: '已添加到购物车',
      icon: 'success'
    })

    // 跳转到购物车页面
    setTimeout(() => {
      wx.switchTab({
        url: '/pages/cart/index'
      })
    }, 1500)
  }
}) 