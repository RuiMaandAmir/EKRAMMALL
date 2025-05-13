const app = getApp()

Page({
  data: {
    order: null,
    refundType: 'refund',
    reason: '',
    customReason: '',
    amount: '',
    desc: '',
    images: [],
    reasonList: [
      { label: '商品质量问题', value: 'quality' },
      { label: '商品与描述不符', value: 'description' },
      { label: '商品损坏', value: 'damage' },
      { label: '商品错发/漏发', value: 'wrong' },
      { label: '商品不喜欢', value: 'unlike' },
      { label: '其他原因', value: 'other' }
    ]
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
          this.setData({
            order: res.data,
            amount: res.data.payment_amount
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

  selectRefundType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      refundType: type
    })
  },

  selectReason(e) {
    const reason = e.currentTarget.dataset.reason
    this.setData({
      reason: reason,
      customReason: ''
    })
  },

  inputCustomReason(e) {
    this.setData({
      customReason: e.detail.value
    })
  },

  inputAmount(e) {
    const amount = e.detail.value
    const maxAmount = this.data.order.payment_amount
    if (amount > maxAmount) {
      wx.showToast({
        title: '退款金额不能超过订单金额',
        icon: 'none'
      })
      this.setData({
        amount: maxAmount
      })
    } else {
      this.setData({
        amount: amount
      })
    }
  },

  inputDesc(e) {
    this.setData({
      desc: e.detail.value
    })
  },

  chooseImage() {
    wx.chooseImage({
      count: 9 - this.data.images.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({
          images: [...this.data.images, ...res.tempFilePaths]
        })
      }
    })
  },

  deleteImage(e) {
    const index = e.currentTarget.dataset.index
    const images = this.data.images
    images.splice(index, 1)
    this.setData({
      images
    })
  },

  async submitRefund() {
    const { order, refundType, reason, customReason, amount, desc, images } = this.data

    // 验证表单
    if (!reason) {
      wx.showToast({
        title: '请选择退款原因',
        icon: 'none'
      })
      return
    }

    if (reason === 'other' && !customReason) {
      wx.showToast({
        title: '请输入其他原因',
        icon: 'none'
      })
      return
    }

    if (!amount) {
      wx.showToast({
        title: '请输入退款金额',
        icon: 'none'
      })
      return
    }

    try {
      // 上传图片
      const uploadedImages = []
      for (const image of images) {
        const res = await this.uploadImage(image)
        uploadedImages.push(res)
      }

      // 提交退款申请
      const refundData = {
        order: order.order_number,
        type: refundType,
        reason: reason === 'other' ? customReason : reason,
        amount: amount,
        desc: desc,
        images: uploadedImages
      }

      await wx.request({
        url: `${app.globalData.baseUrl}/api/orders/${order.order_number}/refund/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        data: refundData
      })

      wx.showToast({
        title: '提交成功',
        icon: 'success'
      })

      // 返回上一页
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      console.error('提交退款申请失败:', error)
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