const app = getApp()

Page({
  data: {
    product: null,
    loading: true
  },

  onLoad(options) {
    this.loadProductDetail(options.id)
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
            loading: false
          })
        }
      },
      fail: (error) => {
        console.error('加载商品详情失败:', error)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
        this.setData({ loading: false })
      }
    })
  },

  shareProduct() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  onShareAppMessage() {
    return {
      title: this.data.product.name,
      path: `/pages/distributor/products/detail/index?id=${this.data.product.id}&distributor_id=${app.globalData.userInfo.id}`,
      imageUrl: this.data.product.images[0]
    }
  },

  onShareTimeline() {
    return {
      title: this.data.product.name,
      query: `id=${this.data.product.id}&distributor_id=${app.globalData.userInfo.id}`,
      imageUrl: this.data.product.images[0]
    }
  },

  navigateToBuy() {
    wx.navigateTo({
      url: `/pages/distributor/products/buy/index?id=${this.data.product.id}`
    })
  }
}) 