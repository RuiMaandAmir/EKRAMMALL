const app = getApp()

Page({
  data: {
    balance: 0,
    minWithdrawAmount: 100,
    withdrawFee: 0.6,
    amount: '',
    accounts: [],
    accountIndex: -1,
    selectedAccount: null,
    canSubmit: false
  },

  onLoad() {
    this.loadData()
  },

  // 加载数据
  async loadData() {
    try {
      wx.showLoading({ title: '加载中' })
      
      // 获取可提现余额
      const balanceRes = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/balance/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (balanceRes.statusCode === 200) {
        this.setData({
          balance: balanceRes.data.available_balance
        })
      }

      // 获取提现账户列表
      const accountsRes = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/accounts/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (accountsRes.statusCode === 200) {
        this.setData({
          accounts: accountsRes.data
        })
      }
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

  // 输入提现金额
  onAmountInput(e) {
    const amount = e.detail.value
    this.setData({ amount })
    this.checkSubmitStatus()
  },

  // 选择提现账户
  onAccountChange(e) {
    const index = e.detail.value
    const selectedAccount = this.data.accounts[index]
    this.setData({
      accountIndex: index,
      selectedAccount
    })
    this.checkSubmitStatus()
  },

  // 检查提交状态
  checkSubmitStatus() {
    const { amount, balance, minWithdrawAmount, selectedAccount } = this.data
    const amountNum = parseFloat(amount)
    
    const canSubmit = amountNum > 0 && 
                     amountNum <= balance && 
                     amountNum >= minWithdrawAmount && 
                     selectedAccount !== null
    
    this.setData({ canSubmit })
  },

  // 提交提现申请
  async submitWithdraw() {
    if (!this.data.canSubmit) return

    try {
      wx.showLoading({ title: '提交中' })
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/withdraw/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: {
          amount: this.data.amount,
          account_id: this.data.selectedAccount.id
        }
      })

      if (res.statusCode === 201) {
        wx.showToast({
          title: '提交成功',
          icon: 'success'
        })
        
        // 返回上一页
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      } else {
        throw new Error(res.data.message || '提交失败')
      }
    } catch (error) {
      console.error('提现申请失败:', error)
      wx.showToast({
        title: error.message || '提交失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  }
}) 