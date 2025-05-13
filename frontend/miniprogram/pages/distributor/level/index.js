const app = getApp()

Page({
  data: {
    currentLevel: null,
    nextLevelProgress: {
      team_size: { current: 0, required: 0, progress: 0 },
      sales: { current: 0, required: 0, progress: 0 },
      orders: { current: 0, required: 0, progress: 0 },
      commission: { current: 0, required: 0, progress: 0 }
    }
  },

  onLoad() {
    this.loadLevelInfo()
  },

  onShow() {
    this.loadLevelInfo()
  },

  loadLevelInfo() {
    wx.showLoading({
      title: '加载中...'
    })

    wx.request({
      url: `${app.globalData.baseUrl}/api/promotions/distribution-level/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            currentLevel: res.data.current_level,
            nextLevelProgress: res.data.next_level_progress
          })
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'error'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'error'
        })
      },
      complete: () => {
        wx.hideLoading()
      }
    })
  },

  // 手动检查升级
  checkUpgrade() {
    wx.showLoading({
      title: '检查中...'
    })

    wx.request({
      url: `${app.globalData.baseUrl}/api/promotions/distribution-level/update/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          if (res.data.message === '等级更新成功') {
            wx.showToast({
              title: '升级成功',
              icon: 'success'
            })
            this.loadLevelInfo()
          } else {
            wx.showToast({
              title: res.data.message,
              icon: 'none'
            })
          }
        } else {
          wx.showToast({
            title: '操作失败',
            icon: 'error'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'error'
        })
      },
      complete: () => {
        wx.hideLoading()
      }
    })
  }
}) 