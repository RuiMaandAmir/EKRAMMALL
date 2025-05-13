const app = getApp()

Page({
  data: {
    accounts: []
  },

  onLoad() {
    this.loadAccounts()
  },

  onShow() {
    this.loadAccounts()
  },

  // 加载账户列表
  async loadAccounts() {
    try {
      wx.showLoading({ title: '加载中' })
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/accounts/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (res.statusCode === 200) {
        this.setData({
          accounts: res.data
        })
      }
    } catch (error) {
      console.error('加载账户列表失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 添加账户
  addAccount() {
    wx.navigateTo({
      url: '/pages/distributor/account/edit/index'
    })
  },

  // 编辑账户
  editAccount(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/distributor/account/edit/index?id=${id}`
    })
  },

  // 删除账户
  deleteAccount(e) {
    const id = e.currentTarget.dataset.id
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该提现账户吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '删除中' })
            
            const deleteRes = await wx.request({
              url: `${app.globalData.baseUrl}/api/distributor/accounts/${id}/`,
              method: 'DELETE',
              header: {
                'Authorization': `Bearer ${app.globalData.token}`
              }
            })
            
            if (deleteRes.statusCode === 204) {
              wx.showToast({
                title: '删除成功',
                icon: 'success'
              })
              this.loadAccounts()
            } else {
              throw new Error(deleteRes.data.message || '删除失败')
            }
          } catch (error) {
            console.error('删除账户失败:', error)
            wx.showToast({
              title: error.message || '删除失败',
              icon: 'error'
            })
          } finally {
            wx.hideLoading()
          }
        }
      }
    })
  }
}) 