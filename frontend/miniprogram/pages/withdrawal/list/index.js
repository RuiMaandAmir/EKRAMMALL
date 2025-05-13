const app = getApp()

Page({
  data: {
    availableAmount: 0,
    totalWithdrawn: 0,
    withdrawals: [],
    statusMap: {
      'pending': '待处理',
      'approved': '已批准',
      'rejected': '已拒绝',
      'completed': '已完成'
    }
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.loadData()
    wx.stopPullDownRefresh()
  },

  async loadData() {
    try {
      // 获取分销商信息
      const distributorRes = await wx.cloud.callContainer({
        path: '/api/distributors/me/',
        method: 'GET',
        header: {
          'X-WX-SERVICE': 'django',
          'Authorization': `Bearer ${wx.getStorageSync('token')}`
        }
      })
      
      this.setData({
        availableAmount: distributorRes.data.balance,
        totalWithdrawn: distributorRes.data.total_withdrawn || 0
      })

      // 获取提现记录
      const withdrawalsRes = await wx.cloud.callContainer({
        path: '/api/withdrawals/',
        method: 'GET',
        header: {
          'X-WX-SERVICE': 'django',
          'Authorization': `Bearer ${wx.getStorageSync('token')}`
        }
      })
      
      // 处理提现记录数据
      const withdrawals = withdrawalsRes.data.map(item => ({
        ...item,
        statusText: this.data.statusMap[item.status],
        created_at: this.formatDate(item.created_at)
      }))
      
      this.setData({ withdrawals })
    } catch (error) {
      console.error('加载数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  formatDate(dateStr) {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  },

  onItemTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/withdrawal/detail/index?id=${id}`
    })
  },

  onApplyTap() {
    if (this.data.availableAmount < 10) {
      wx.showToast({
        title: '可提现金额不足10元',
        icon: 'none'
      })
      return
    }
    
    wx.navigateTo({
      url: '/pages/withdrawal/apply/index'
    })
  }
}) 