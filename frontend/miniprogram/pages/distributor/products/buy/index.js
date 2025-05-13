const app = getApp()

Page({
  data: {
    product: null,
    quantity: 1,
    address: null,
    contactName: '',
    contactPhone: '',
    remark: '',
    shippingFee: 0
  },

  onLoad(options) {
    this.loadProductDetail(options.id)
    this.loadDefaultAddress()
  },

  loadProductDetail(id) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/distributor-products/${id}/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            product: res.data,
            shippingFee: res.data.shipping_fee || 0
          })
        }
      },
      fail: (error) => {
        console.error('加载商品详情失败:', error)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    })
  },

  loadDefaultAddress() {
    wx.request({
      url: `${app.globalData.baseUrl}/api/addresses/default/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          this.setData({
            address: res.data,
            contactName: res.data.contact_name,
            contactPhone: res.data.contact_phone
          })
        }
      }
    })
  },

  decreaseQuantity() {
    if (this.data.quantity > 1) {
      this.setData({
        quantity: this.data.quantity - 1
      })
    }
  },

  increaseQuantity() {
    this.setData({
      quantity: this.data.quantity + 1
    })
  },

  onQuantityChange(e) {
    const quantity = parseInt(e.detail.value) || 1
    this.setData({
      quantity: quantity < 1 ? 1 : quantity
    })
  },

  selectAddress() {
    wx.navigateTo({
      url: '/pages/address/list/index?select=1'
    })
  },

  onContactNameChange(e) {
    this.setData({
      contactName: e.detail.value
    })
  },

  onContactPhoneChange(e) {
    this.setData({
      contactPhone: e.detail.value
    })
  },

  onRemarkChange(e) {
    this.setData({
      remark: e.detail.value
    })
  },

  submitOrder() {
    if (!this.data.address) {
      wx.showToast({
        title: '请选择收货地址',
        icon: 'none'
      })
      return
    }

    if (!this.data.contactName) {
      wx.showToast({
        title: '请输入联系人姓名',
        icon: 'none'
      })
      return
    }

    if (!this.data.contactPhone) {
      wx.showToast({
        title: '请输入联系电话',
        icon: 'none'
      })
      return
    }

    wx.request({
      url: `${app.globalData.baseUrl}/api/distributor-orders/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: {
        product_id: this.data.product.id,
        quantity: this.data.quantity,
        address_id: this.data.address.id,
        contact_name: this.data.contactName,
        contact_phone: this.data.contactPhone,
        remark: this.data.remark
      },
      success: (res) => {
        if (res.statusCode === 201) {
          wx.navigateTo({
            url: `/pages/order/payment/index?order_number=${res.data.order_number}`
          })
        }
      },
      fail: (error) => {
        console.error('提交订单失败:', error)
        wx.showToast({
          title: '提交失败',
          icon: 'none'
        })
      }
    })
  }
}) 