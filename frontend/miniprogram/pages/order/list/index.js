const app = getApp()

Page({
  data: {
    tabs: ['全部', '待付款', '待发货', '待收货', '已完成'],
    activeTab: 0,
    statusMap: {
      0: '', // 全部
      1: 'pending', // 待付款
      2: 'paid', // 待发货
      3: 'shipped', // 待收货
      4: 'completed' // 已完成
    },
    orders: [],
    page: 1,
    loading: false,
    hasMore: true
  },

  onLoad() {
    this.loadOrders()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      orders: [],
      hasMore: true
    })
    this.loadOrders().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadOrders()
    }
  },

  switchTab(e) {
    const index = e.currentTarget.dataset.index
    if (index === this.data.activeTab) return
    
    this.setData({
      activeTab: index,
      page: 1,
      orders: [],
      hasMore: true
    })
    this.loadOrders()
  },

  async loadOrders() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    try {
      const status = this.data.statusMap[this.data.activeTab]
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/orders/`,
        method: 'GET',
        data: {
          status,
          page: this.data.page
        },
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })

      if (res.statusCode === 200) {
        const orders = res.data.results
        this.setData({
          orders: [...this.data.orders, ...orders],
          page: this.data.page + 1,
          hasMore: !!res.data.next
        })
      } else {
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载订单失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  async cancelOrder(e) {
    const orderId = e.currentTarget.dataset.id
    try {
      const res = await wx.showModal({
        title: '提示',
        content: '确定要取消该订单吗？'
      })

      if (res.confirm) {
        await wx.request({
          url: `${app.globalData.baseUrl}/api/orders/${orderId}/cancel/`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${app.globalData.token}`
          }
        })

        wx.showToast({
          title: '取消成功',
          icon: 'success'
        })

        // 刷新订单列表
        this.setData({
          page: 1,
          orders: [],
          hasMore: true
        })
        this.loadOrders()
      }
    } catch (error) {
      console.error('取消订单失败:', error)
      wx.showToast({
        title: '取消失败',
        icon: 'none'
      })
    }
  },

  async payOrder(e) {
    const orderId = e.currentTarget.dataset.id
    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/orders/${orderId}/pay/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })

      if (res.statusCode === 200) {
        const paymentParams = res.data
        await wx.requestPayment({
          ...paymentParams,
          success: () => {
            wx.showToast({
              title: '支付成功',
              icon: 'success'
            })
            // 刷新订单列表
            this.setData({
              page: 1,
              orders: [],
              hasMore: true
            })
            this.loadOrders()
          },
          fail: () => {
            wx.showToast({
              title: '支付失败',
              icon: 'none'
            })
          }
        })
      }
    } catch (error) {
      console.error('支付失败:', error)
      wx.showToast({
        title: '支付失败',
        icon: 'none'
      })
    }
  },

  async confirmOrder(e) {
    const orderId = e.currentTarget.dataset.id
    try {
      const res = await wx.showModal({
        title: '提示',
        content: '确认已收到商品？'
      })

      if (res.confirm) {
        await wx.request({
          url: `${app.globalData.baseUrl}/api/orders/${orderId}/confirm/`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${app.globalData.token}`
          }
        })

        wx.showToast({
          title: '确认成功',
          icon: 'success'
        })

        // 刷新订单列表
        this.setData({
          page: 1,
          orders: [],
          hasMore: true
        })
        this.loadOrders()
      }
    } catch (error) {
      console.error('确认收货失败:', error)
      wx.showToast({
        title: '确认失败',
        icon: 'none'
      })
    }
  },

  async deleteOrder(e) {
    const orderId = e.currentTarget.dataset.id
    try {
      const res = await wx.showModal({
        title: '提示',
        content: '确定要删除该订单吗？'
      })

      if (res.confirm) {
        await wx.request({
          url: `${app.globalData.baseUrl}/api/orders/${orderId}/`,
          method: 'DELETE',
          header: {
            'Authorization': `Bearer ${app.globalData.token}`
          }
        })

        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })

        // 刷新订单列表
        this.setData({
          page: 1,
          orders: [],
          hasMore: true
        })
        this.loadOrders()
      }
    } catch (error) {
      console.error('删除订单失败:', error)
      wx.showToast({
        title: '删除失败',
        icon: 'none'
      })
    }
  },

  viewLogistics(e) {
    const orderId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/order/logistics/index?id=${orderId}`
    })
  },

  buyAgain(e) {
    const orderId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/order/detail/index?id=${orderId}`
    })
  }
}) 