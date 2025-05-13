const app = getApp()

Page({
  data: {
    user: null,
    level: null,
    stats: {
      today_commission: 0,
      month_commission: 0,
      total_orders: 0
    },
    levels: []
  },

  onShow() {
    this.loadData()
  },

  loadData() {
    Promise.all([
      this.getUserInfo(),
      this.getDistributorInfo(),
      this.getLevels()
    ]).catch(error => {
      console.error('加载数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  getUserInfo() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/users/me/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            user: res.data
          })
        }
      }
    })
  },

  getDistributorInfo() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributors/me/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            level: res.data.level,
            stats: {
              today_commission: res.data.today_commission,
              month_commission: res.data.month_commission,
              total_orders: res.data.total_orders
            }
          })
        }
      }
    })
  },

  getLevels() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributor-levels/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            levels: res.data
          })
        }
      }
    })
  },

  navigateTo(e) {
    const url = e.currentTarget.dataset.url
    wx.navigateTo({
      url
    })
  }
}) 