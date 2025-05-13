const app = getApp()

Page({
  data: {
    order: null,
    rating: {},
    reviews: {},
    images: {}
  },

  onLoad(options) {
    const { order_number } = options
    if (order_number) {
      this.getOrderDetail(order_number)
    }
  },

  getOrderDetail(order_number) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/orders/${order_number}/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          // 初始化评价数据
          const rating = {}
          const reviews = {}
          const images = {}
          res.data.items.forEach(item => {
            rating[item.id] = 5 // 默认5星
            reviews[item.id] = ''
            images[item.id] = []
          })

          this.setData({
            order: res.data,
            rating,
            reviews,
            images
          })
        } else {
          wx.showToast({
            title: '获取订单信息失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  selectRating(e) {
    const { itemId, rating } = e.currentTarget.dataset
    const ratingData = this.data.rating
    ratingData[itemId] = rating
    this.setData({
      rating: ratingData
    })
  },

  inputReview(e) {
    const { itemId } = e.currentTarget.dataset
    const reviews = this.data.reviews
    reviews[itemId] = e.detail.value
    this.setData({
      reviews
    })
  },

  chooseImage(e) {
    const { itemId } = e.currentTarget.dataset
    const currentImages = this.data.images[itemId] || []
    
    wx.chooseImage({
      count: 9 - currentImages.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const images = this.data.images
        images[itemId] = [...currentImages, ...res.tempFilePaths]
        this.setData({
          images
        })
      }
    })
  },

  deleteImage(e) {
    const { itemId, index } = e.currentTarget.dataset
    const images = this.data.images
    images[itemId].splice(index, 1)
    this.setData({
      images
    })
  },

  async submitReview() {
    const { order, rating, reviews, images } = this.data

    try {
      // 上传图片
      const uploadedImages = {}
      for (const itemId in images) {
        uploadedImages[itemId] = []
        for (const image of images[itemId]) {
          const url = await this.uploadImage(image)
          uploadedImages[itemId].push(url)
        }
      }

      // 提交评价
      const reviewData = order.items.map(item => ({
        order_item: item.id,
        rating: rating[item.id],
        content: reviews[item.id],
        images: uploadedImages[item.id]
      }))

      await wx.request({
        url: `${app.globalData.baseUrl}/api/orders/${order.order_number}/review/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: reviewData
      })

      wx.showToast({
        title: '评价成功',
        icon: 'success'
      })

      // 返回上一页
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      console.error('提交评价失败:', error)
      wx.showToast({
        title: '提交失败',
        icon: 'none'
      })
    }
  },

  uploadImage(filePath) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${app.globalData.baseUrl}/api/upload/`,
        filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(res.data).url)
          } else {
            reject(new Error('上传失败'))
          }
        },
        fail: reject
      })
    })
  }
}) 