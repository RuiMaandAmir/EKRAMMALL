const app = getApp()

Page({
  data: {
    product: null,
    selectedVariant: null,
    quantity: 1,
    loading: true,
    error: null
  },

  onLoad: function(options) {
    if (options.id) {
      this.loadProductDetail(options.id)
    }
  },

  loadProductDetail: function(productId) {
    this.setData({ loading: true, error: null })
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/products/${productId}/`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          const product = res.data
          // 如果有变体，选择默认变体
          const selectedVariant = product.variants && product.variants.length > 0 
            ? product.variants.find(v => v.is_default) || product.variants[0]
            : null
            
          this.setData({
            product,
            selectedVariant,
            loading: false
          })
        } else {
          this.setData({
            error: '加载商品信息失败',
            loading: false
          })
        }
      },
      fail: () => {
        this.setData({
          error: '网络错误，请稍后重试',
          loading: false
        })
      }
    })
  },

  selectVariant: function(e) {
    const variantId = e.currentTarget.dataset.id
    const variant = this.data.product.variants.find(v => v.id === variantId)
    if (variant) {
      this.setData({ selectedVariant: variant })
    }
  },

  changeQuantity: function(e) {
    const type = e.currentTarget.dataset.type
    let quantity = this.data.quantity
    
    if (type === 'minus' && quantity > 1) {
      quantity--
    } else if (type === 'plus') {
      quantity++
    }
    
    this.setData({ quantity })
  },

  addToCart: function() {
    if (!this.data.product) return
    
    const cartItem = {
      productId: this.data.product.id,
      variantId: this.data.selectedVariant?.id,
      quantity: this.data.quantity,
      name: this.data.product.name,
      price: this.data.selectedVariant?.price || this.data.product.price,
      image: this.data.product.image
    }
    
    app.addToCart(cartItem)
    wx.showToast({
      title: '已加入购物车',
      icon: 'success'
    })
  },

  buyNow: function() {
    if (!this.data.product) return
    
    const orderItem = {
      productId: this.data.product.id,
      variantId: this.data.selectedVariant?.id,
      quantity: this.data.quantity,
      name: this.data.product.name,
      price: this.data.selectedVariant?.price || this.data.product.price,
      image: this.data.product.image
    }
    
    app.setTempOrder([orderItem])
    wx.navigateTo({
      url: '/pages/order/confirm/index'
    })
  }
}) 