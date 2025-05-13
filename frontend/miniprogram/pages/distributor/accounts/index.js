const app = getApp()
const { request } = require('../../../utils/request')

Page({
  data: {
    accounts: [],
    showDialog: false,
    showDeleteDialog: false,
    isEdit: false,
    currentAccountId: null,
    accountType: 'wechat',
    accountName: '',
    accountNumber: '',
    bankName: '',
    branchName: ''
  },

  onLoad() {
    this.loadAccounts()
  },

  // 加载账户列表
  async loadAccounts() {
    try {
      const res = await request({
        url: '/distributor/accounts/'
      })

      this.setData({
        accounts: res.data
      })
    } catch (error) {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 显示添加账户弹窗
  showAddDialog() {
    this.setData({
      showDialog: true,
      isEdit: false,
      accountType: 'wechat',
      accountName: '',
      accountNumber: '',
      bankName: '',
      branchName: ''
    })
  },

  // 显示编辑账户弹窗
  editAccount(e) {
    const id = e.currentTarget.dataset.id
    const account = this.data.accounts.find(item => item.id === id)

    this.setData({
      showDialog: true,
      isEdit: true,
      currentAccountId: id,
      accountType: account.type,
      accountName: account.name,
      accountNumber: account.number,
      bankName: account.bank_name || '',
      branchName: account.branch_name || ''
    })
  },

  // 隐藏弹窗
  hideDialog() {
    this.setData({
      showDialog: false
    })
  },

  // 账户类型变化
  onTypeChange(e) {
    this.setData({
      accountType: e.detail.value
    })
  },

  // 账户名称输入
  onNameInput(e) {
    this.setData({
      accountName: e.detail.value
    })
  },

  // 账户号码输入
  onNumberInput(e) {
    this.setData({
      accountNumber: e.detail.value
    })
  },

  // 银行名称输入
  onBankInput(e) {
    this.setData({
      bankName: e.detail.value
    })
  },

  // 支行名称输入
  onBranchInput(e) {
    this.setData({
      branchName: e.detail.value
    })
  },

  // 保存账户
  async saveAccount() {
    // 表单验证
    if (!this.data.accountName) {
      wx.showToast({
        title: '请输入账户名称',
        icon: 'none'
      })
      return
    }

    if (!this.data.accountNumber) {
      wx.showToast({
        title: '请输入账户号码',
        icon: 'none'
      })
      return
    }

    if (this.data.accountType === 'bank') {
      if (!this.data.bankName) {
        wx.showToast({
          title: '请输入开户银行',
          icon: 'none'
        })
        return
      }
    }

    try {
      wx.showLoading({
        title: '保存中'
      })

      const data = {
        type: this.data.accountType,
        name: this.data.accountName,
        number: this.data.accountNumber
      }

      if (this.data.accountType === 'bank') {
        data.bank_name = this.data.bankName
        data.branch_name = this.data.branchName
      }

      if (this.data.isEdit) {
        await request({
          url: `/distributor/accounts/${this.data.currentAccountId}/`,
          method: 'PUT',
          data
        })
      } else {
        await request({
          url: '/distributor/accounts/',
          method: 'POST',
          data
        })
      }

      wx.hideLoading()
      this.hideDialog()
      this.loadAccounts()

      wx.showToast({
        title: '保存成功',
        icon: 'success'
      })
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: '保存失败',
        icon: 'none'
      })
    }
  },

  // 显示删除确认弹窗
  deleteAccount(e) {
    const id = e.currentTarget.dataset.id
    this.setData({
      showDeleteDialog: true,
      currentAccountId: id
    })
  },

  // 隐藏删除确认弹窗
  hideDeleteDialog() {
    this.setData({
      showDeleteDialog: false
    })
  },

  // 确认删除
  async confirmDelete() {
    try {
      wx.showLoading({
        title: '删除中'
      })

      await request({
        url: `/distributor/accounts/${this.data.currentAccountId}/`,
        method: 'DELETE'
      })

      wx.hideLoading()
      this.hideDeleteDialog()
      this.loadAccounts()

      wx.showToast({
        title: '删除成功',
        icon: 'success'
      })
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: '删除失败',
        icon: 'none'
      })
    }
  }
}) 