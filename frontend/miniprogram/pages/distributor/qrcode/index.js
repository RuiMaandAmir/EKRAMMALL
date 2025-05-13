const app = getApp()

Page({
  data: {
    qrcodeUrl: '',
    shareLink: '',
    customerCount: 0,
    orderCount: 0,
    totalCommission: 0
  },

  onLoad() {
    this.loadData()
  },

  loadData() {
    Promise.all([
      this.getQrcode(),
      this.getShareLink(),
      this.getStats()
    ]).catch(error => {
      console.error('加载数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  getQrcode() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributors/qrcode/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            qrcodeUrl: res.data.qrcode_url
          })
        }
      }
    })
  },

  getShareLink() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributors/share-link/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            shareLink: res.data.share_link
          })
        }
      }
    })
  },

  getStats() {
    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributors/stats/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            customerCount: res.data.customer_count,
            orderCount: res.data.order_count,
            totalCommission: res.data.total_commission
          })
        }
      }
    })
  },

  copyLink() {
    wx.setClipboardData({
      data: this.data.shareLink,
      success: () => {
        wx.showToast({
          title: '复制成功',
          icon: 'success'
        })
      }
    })
  },

  onShareAppMessage() {
    return {
      title: '快来加入我的分销团队吧！',
      path: `/pages/index/index?distributor_id=${app.globalData.userInfo.id}`,
      imageUrl: this.data.qrcodeUrl
    }
  }
}) 