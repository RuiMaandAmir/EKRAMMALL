const app = getApp()

Page({
  data: {
    distributorInfo: {
      level_name: '',
      code: '',
      created_at: '',
      default_commission_rate: 0,
      max_commission_rate: 0,
      min_withdraw_amount: 0,
      promotion_link: '',
      qrcode_url: ''
    },
    settings: {
      notification: true,
      auto_withdraw: false
    },
    showQuitDialog: false
  },

  onLoad() {
    this.loadDistributorInfo()
    this.loadSettings()
  },

  // 加载分销商信息
  async loadDistributorInfo() {
    try {
      wx.showLoading({ title: '加载中' })
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/info/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (res.statusCode === 200) {
        this.setData({
          distributorInfo: res.data
        })
      }
    } catch (error) {
      console.error('加载分销商信息失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 加载设置
  async loadSettings() {
    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/settings/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (res.statusCode === 200) {
        this.setData({
          settings: res.data
        })
      }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  },

  // 生成推广海报
  async generatePoster() {
    try {
      wx.showLoading({ title: '生成中' })
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/poster/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (res.statusCode === 200) {
        wx.previewImage({
          urls: [res.data.poster_url],
          current: res.data.poster_url
        })
      }
    } catch (error) {
      console.error('生成海报失败:', error)
      wx.showToast({
        title: '生成失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 复制推广链接
  copyLink() {
    wx.setClipboardData({
      data: this.data.distributorInfo.promotion_link,
      success: () => {
        wx.showToast({
          title: '复制成功',
          icon: 'success'
        })
      }
    })
  },

  // 切换消息通知
  async toggleNotification(e) {
    const notification = e.detail.value
    try {
      await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/settings/`,
        method: 'PATCH',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: {
          notification
        }
      })
      
      this.setData({
        'settings.notification': notification
      })
    } catch (error) {
      console.error('更新设置失败:', error)
      wx.showToast({
        title: '更新失败',
        icon: 'error'
      })
    }
  },

  // 切换自动提现
  async toggleAutoWithdraw(e) {
    const autoWithdraw = e.detail.value
    try {
      await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/settings/`,
        method: 'PATCH',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: {
          auto_withdraw: autoWithdraw
        }
      })
      
      this.setData({
        'settings.auto_withdraw': autoWithdraw
      })
    } catch (error) {
      console.error('更新设置失败:', error)
      wx.showToast({
        title: '更新失败',
        icon: 'error'
      })
    }
  },

  // 显示退出确认弹窗
  showQuitDialog() {
    this.setData({
      showQuitDialog: true
    })
  },

  // 隐藏退出确认弹窗
  hideQuitDialog() {
    this.setData({
      showQuitDialog: false
    })
  },

  // 退出分销
  async quitDistributor() {
    try {
      wx.showLoading({ title: '处理中' })
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/quit/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (res.statusCode === 200) {
        wx.showToast({
          title: '退出成功',
          icon: 'success'
        })
        
        // 返回上一页
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (error) {
      console.error('退出分销失败:', error)
      wx.showToast({
        title: '退出失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
      this.hideQuitDialog()
    }
  }
}) 