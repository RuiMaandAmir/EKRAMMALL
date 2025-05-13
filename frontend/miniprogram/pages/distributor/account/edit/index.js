const app = getApp()

Page({
  data: {
    id: null,
    type: 'wechat',
    wechatAccount: '',
    wechatName: '',
    bankName: '',
    branchName: '',
    bankAccount: '',
    cardholder: '',
    canSubmit: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: options.id })
      this.loadAccountDetail()
    }
  },

  // 加载账户详情
  async loadAccountDetail() {
    try {
      wx.showLoading({ title: '加载中' })
      
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/distributor/accounts/${this.data.id}/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        }
      })
      
      if (res.statusCode === 200) {
        const account = res.data
        this.setData({
          type: account.type,
          wechatAccount: account.type === 'wechat' ? account.number : '',
          wechatName: account.type === 'wechat' ? account.name : '',
          bankName: account.type === 'bank' ? account.bank_name : '',
          branchName: account.type === 'bank' ? account.branch_name : '',
          bankAccount: account.type === 'bank' ? account.number : '',
          cardholder: account.type === 'bank' ? account.cardholder : ''
        })
        this.checkSubmitStatus()
      }
    } catch (error) {
      console.error('加载账户详情失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 选择账户类型
  selectType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ type })
    this.checkSubmitStatus()
  },

  // 输入微信账号
  onWechatAccountInput(e) {
    this.setData({ wechatAccount: e.detail.value })
    this.checkSubmitStatus()
  },

  // 输入微信昵称
  onWechatNameInput(e) {
    this.setData({ wechatName: e.detail.value })
    this.checkSubmitStatus()
  },

  // 输入银行名称
  onBankNameInput(e) {
    this.setData({ bankName: e.detail.value })
    this.checkSubmitStatus()
  },

  // 输入支行名称
  onBranchNameInput(e) {
    this.setData({ branchName: e.detail.value })
    this.checkSubmitStatus()
  },

  // 输入银行卡号
  onBankAccountInput(e) {
    this.setData({ bankAccount: e.detail.value })
    this.checkSubmitStatus()
  },

  // 输入持卡人姓名
  onCardholderInput(e) {
    this.setData({ cardholder: e.detail.value })
    this.checkSubmitStatus()
  },

  // 检查提交状态
  checkSubmitStatus() {
    const { type, wechatAccount, wechatName, bankName, bankAccount, cardholder } = this.data
    
    let canSubmit = false
    if (type === 'wechat') {
      canSubmit = wechatAccount.trim() !== '' && wechatName.trim() !== ''
    } else {
      canSubmit = bankName.trim() !== '' && bankAccount.trim() !== '' && cardholder.trim() !== ''
    }
    
    this.setData({ canSubmit })
  },

  // 提交表单
  async submitForm() {
    if (!this.data.canSubmit) return

    try {
      wx.showLoading({ title: '提交中' })
      
      const data = {
        type: this.data.type
      }
      
      if (this.data.type === 'wechat') {
        data.number = this.data.wechatAccount.trim()
        data.name = this.data.wechatName.trim()
      } else {
        data.bank_name = this.data.bankName.trim()
        data.branch_name = this.data.branchName.trim()
        data.number = this.data.bankAccount.trim()
        data.cardholder = this.data.cardholder.trim()
      }
      
      const url = this.data.id 
        ? `${app.globalData.baseUrl}/api/distributor/accounts/${this.data.id}/`
        : `${app.globalData.baseUrl}/api/distributor/accounts/`
      
      const method = this.data.id ? 'PUT' : 'POST'
      
      const res = await wx.request({
        url,
        method,
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data
      })
      
      if ((method === 'POST' && res.statusCode === 201) || 
          (method === 'PUT' && res.statusCode === 200)) {
        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      } else {
        throw new Error(res.data.message || '保存失败')
      }
    } catch (error) {
      console.error('保存账户失败:', error)
      wx.showToast({
        title: error.message || '保存失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  }
}) 