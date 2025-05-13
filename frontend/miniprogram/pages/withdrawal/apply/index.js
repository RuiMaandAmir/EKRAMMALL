const app = getApp()

Page({
  data: {
    availableAmount: 0,
    amount: '',
    bankName: '',
    bankAccount: '',
    accountHolder: '',
    isFormValid: false
  },

  onLoad() {
    this.loadData()
  },

  async loadData() {
    try {
      const res = await wx.cloud.callContainer({
        path: '/api/distributors/me/',
        method: 'GET',
        header: {
          'X-WX-SERVICE': 'django',
          'Authorization': `Bearer ${wx.getStorageSync('token')}`
        }
      })
      
      this.setData({
        availableAmount: res.data.balance
      })
    } catch (error) {
      console.error('加载数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  onAmountInput(e) {
    this.setData({
      amount: e.detail.value
    })
    this.validateForm()
  },

  onBankNameInput(e) {
    this.setData({
      bankName: e.detail.value
    })
    this.validateForm()
  },

  onBankAccountInput(e) {
    this.setData({
      bankAccount: e.detail.value
    })
    this.validateForm()
  },

  onAccountHolderInput(e) {
    this.setData({
      accountHolder: e.detail.value
    })
    this.validateForm()
  },

  validateForm() {
    const { amount, bankName, bankAccount, accountHolder } = this.data
    
    // 验证所有字段都已填写
    const isFormFilled = amount && bankName && bankAccount && accountHolder
    
    // 验证金额
    const amountNum = parseFloat(amount)
    const isAmountValid = amountNum >= 10 && amountNum <= this.data.availableAmount
    
    // 验证银行账号
    const isBankAccountValid = /^\d{16,19}$/.test(bankAccount)
    
    // 验证开户人姓名
    const isAccountHolderValid = accountHolder.length >= 2 && accountHolder.length <= 20
    
    this.setData({
      isFormValid: isFormFilled && isAmountValid && isBankAccountValid && isAccountHolderValid
    })
  },

  async onSubmit() {
    if (!this.data.isFormValid) return
    
    try {
      wx.showLoading({
        title: '提交中...',
        mask: true
      })
      
      const res = await wx.cloud.callContainer({
        path: '/api/withdrawals/',
        method: 'POST',
        data: {
          amount: this.data.amount,
          bank_name: this.data.bankName,
          bank_account: this.data.bankAccount,
          account_holder: this.data.accountHolder
        },
        header: {
          'X-WX-SERVICE': 'django',
          'Authorization': `Bearer ${wx.getStorageSync('token')}`
        }
      })
      
      wx.hideLoading()
      
      wx.showToast({
        title: '提交成功',
        icon: 'success'
      })
      
      // 返回上一页
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
      
    } catch (error) {
      wx.hideLoading()
      
      wx.showToast({
        title: error.message || '提交失败',
        icon: 'none'
      })
    }
  }
}) 