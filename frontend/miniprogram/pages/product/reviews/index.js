const app = getApp()

Page({
  data: {
    productId: null,
    reviews: [],
    filter: {
      rating: '',
      sort: 'latest'
    },
    page: 1,
    loading: false,
    hasMore: true
  },

  onLoad(options) {
    const { product_id } = options
    if (product_id) {
      this.setData({
        productId: product_id
      })
      this.loadReviews()
    }
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      reviews: [],
      hasMore: true
    })
    this.loadReviews().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadReviews()
    }
  },

  loadReviews() {
    if (this.data.loading) return Promise.resolve()

    this.setData({
      loading: true
    })

    const { productId, filter, page } = this.data

    return wx.request({
      url: `${app.globalData.baseUrl}/api/products/${productId}/reviews/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: {
        ...filter,
        page
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const reviews = res.data.results.map(review => ({
            ...review,
            show_reply: false,
            reply_content: ''
          }))

          this.setData({
            reviews: page === 1 ? reviews : [...this.data.reviews, ...reviews],
            hasMore: !!res.data.next,
            page: page + 1
          })
        } else {
          wx.showToast({
            title: '获取评价失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({
          loading: false
        })
      }
    })
  },

  selectRating(e) {
    const rating = e.currentTarget.dataset.rating
    this.setData({
      'filter.rating': rating,
      page: 1,
      reviews: [],
      hasMore: true
    })
    this.loadReviews()
  },

  selectSort(e) {
    const sort = e.currentTarget.dataset.sort
    this.setData({
      'filter.sort': sort,
      page: 1,
      reviews: [],
      hasMore: true
    })
    this.loadReviews()
  },

  previewImage(e) {
    const { urls, current } = e.currentTarget.dataset
    wx.previewImage({
      urls,
      current
    })
  },

  toggleHelpful(e) {
    const { id } = e.currentTarget.dataset
    const reviews = this.data.reviews
    const index = reviews.findIndex(item => item.id === id)
    if (index === -1) return

    const review = reviews[index]
    const isHelpful = !review.is_helpful

    wx.request({
      url: `${app.globalData.baseUrl}/api/reviews/${id}/helpful/`,
      method: isHelpful ? 'POST' : 'DELETE',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          reviews[index] = {
            ...review,
            is_helpful: isHelpful,
            helpful_count: review.helpful_count + (isHelpful ? 1 : -1)
          }
          this.setData({
            reviews
          })
        } else {
          wx.showToast({
            title: '操作失败',
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

  toggleReply(e) {
    const { id } = e.currentTarget.dataset
    const reviews = this.data.reviews
    const index = reviews.findIndex(item => item.id === id)
    if (index === -1) return

    const review = reviews[index]
    const showReply = !review.show_reply

    if (showReply && !review.replies) {
      this.loadReplies(id)
    }

    reviews[index] = {
      ...review,
      show_reply: showReply
    }
    this.setData({
      reviews
    })
  },

  loadReplies(reviewId) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/reviews/${reviewId}/replies/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const reviews = this.data.reviews
          const index = reviews.findIndex(item => item.id === reviewId)
          if (index !== -1) {
            reviews[index] = {
              ...reviews[index],
              replies: res.data
            }
            this.setData({
              reviews
            })
          }
        }
      }
    })
  },

  inputReply(e) {
    const { id } = e.currentTarget.dataset
    const reviews = this.data.reviews
    const index = reviews.findIndex(item => item.id === id)
    if (index === -1) return

    reviews[index] = {
      ...reviews[index],
      reply_content: e.detail.value
    }
    this.setData({
      reviews
    })
  },

  sendReply(e) {
    const { id } = e.currentTarget.dataset
    const reviews = this.data.reviews
    const index = reviews.findIndex(item => item.id === id)
    if (index === -1) return

    const review = reviews[index]
    const content = review.reply_content.trim()
    if (!content) return

    wx.request({
      url: `${app.globalData.baseUrl}/api/reviews/${id}/replies/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: {
        content
      },
      success: (res) => {
        if (res.statusCode === 201) {
          reviews[index] = {
            ...review,
            reply_content: '',
            reply_count: review.reply_count + 1,
            replies: [...(review.replies || []), res.data]
          }
          this.setData({
            reviews
          })
        } else {
          wx.showToast({
            title: '回复失败',
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
  }
}) 