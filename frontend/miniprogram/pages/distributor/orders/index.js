const app = getApp()

Page({
  data: {
    totalCommission: 0,
    pendingCommission: 0,
    totalOrders: 0,
    currentFilter: 'all',
    orders: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true,
      orders: []
    })
    this.loadData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMoreData()
    }
  },

  // 加载数据
  async loadData() {
    this.setData({ loading: true })
    try {
      const [statsRes, ordersRes] = await Promise.all([
        this.getStats(),
        this.getOrders()
      ])

      if (statsRes.statusCode === 200) {
        this.setData({
          totalCommission: statsRes.data.total_commission,
          pendingCommission: statsRes.data.pending_commission,
          totalOrders: statsRes.data.total_orders
        })
      }

      if (ordersRes.statusCode === 200) {
        this.setData({
          orders: ordersRes.data.results,
          hasMore: ordersRes.data.next !== null
        })
      }
    } catch (error) {
      console.error('加载数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 加载更多数据
  async loadMoreData() {
    if (!this.data.hasMore || this.data.loading) return

    this.setData({ loading: true })
    try {
      const res = await this.getOrders(this.data.page + 1)
      if (res.statusCode === 200) {
        this.setData({
          orders: [...this.data.orders, ...res.data.results],
          page: this.data.page + 1,
          hasMore: res.data.next !== null
        })
      }
    } catch (error) {
      console.error('加载更多数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 获取统计数据
  async getStats() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributor/stats/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      }
    })
  },

  // 获取订单列表
  async getOrders(page = 1) {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributor/orders/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: {
        page,
        page_size: this.data.pageSize,
        status: this.data.currentFilter === 'all' ? '' : this.data.currentFilter
      }
    })
  },

  // 切换筛选条件
  switchFilter(e) {
    const filter = e.currentTarget.dataset.filter
    if (filter === this.data.currentFilter) return

    this.setData({
      currentFilter: filter,
      page: 1,
      hasMore: true,
      orders: []
    })
    this.loadData()
  },

  // 查看订单详情
  viewOrderDetail(e) {
    const orderId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/order/detail/index?id=${orderId}`
    })
  }
}) 