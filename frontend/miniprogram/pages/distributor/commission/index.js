const app = getApp()

Page({
  data: {
    totalCommission: 0,
    monthlyCommission: 0,
    pendingCommission: 0,
    currentDate: '',
    type: 'all',
    commissions: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    // 设置当前日期为当月
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    this.setData({
      currentDate: `${year}-${month}`
    })
    
    this.loadData()
  },

  // 加载数据
  async loadData() {
    try {
      wx.showLoading({ title: '加载中' })
      
      // 获取佣金统计
      const statsRes = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/commission/stats/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (statsRes.statusCode === 200) {
        this.setData({
          totalCommission: statsRes.data.total_commission,
          monthlyCommission: statsRes.data.monthly_commission,
          pendingCommission: statsRes.data.pending_commission
        })
      }

      // 获取佣金列表
      await this.loadCommissions()
    } catch (error) {
      console.error('加载数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 加载佣金列表
  async loadCommissions(isLoadMore = false) {
    if (this.data.loading) return
    
    try {
      this.setData({ loading: true })
      
      const { currentDate, type, page, pageSize } = this.data
      const [year, month] = currentDate.split('-')
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/commission/list/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: {
          year,
          month,
          status: type === 'all' ? '' : type,
          page,
          page_size: pageSize
        }
      })
      
      if (res.statusCode === 200) {
        const { results, count } = res.data
        const commissions = isLoadMore ? [...this.data.commissions, ...results] : results
        
        this.setData({
          commissions,
          hasMore: commissions.length < count,
          page: isLoadMore ? page + 1 : 1
        })
      }
    } catch (error) {
      console.error('加载佣金列表失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 选择日期
  onDateChange(e) {
    this.setData({
      currentDate: e.detail.value,
      page: 1,
      hasMore: true
    })
    this.loadCommissions()
  },

  // 选择类型
  selectType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      type,
      page: 1,
      hasMore: true
    })
    this.loadCommissions()
  },

  // 加载更多
  loadMore() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadCommissions(true)
    }
  },

  // 下拉刷新
  onRefresh() {
    this.setData({
      page: 1,
      hasMore: true
    })
    this.loadData()
  }
}) 