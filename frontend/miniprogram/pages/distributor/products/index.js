const app = getApp()

Page({
  data: {
    products: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    searchKeyword: '',
    currentSort: 'commission'
  },

  onLoad() {
    this.loadProducts()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true,
      products: []
    })
    this.loadProducts().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadProducts()
    }
  },

  onSearch(e) {
    this.setData({
      searchKeyword: e.detail.value
    })
  },

  search() {
    this.setData({
      page: 1,
      hasMore: true,
      products: []
    })
    this.loadProducts()
  },

  setSort(e) {
    const sort = e.currentTarget.dataset.sort
    this.setData({
      currentSort: sort,
      page: 1,
      hasMore: true,
      products: []
    })
    this.loadProducts()
  },

  loadProducts() {
    if (this.data.loading || !this.data.hasMore) return Promise.resolve()

    this.setData({ loading: true })

    return wx.request({
      url: `${app.globalData.baseUrl}/api/distributor-products/`,
      method: 'GET',
      data: {
        page: this.data.page,
        page_size: this.data.pageSize,
        search: this.data.searchKeyword,
        sort: this.data.currentSort
      },
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newProducts = res.data.results
          const hasMore = res.data.next !== null

          this.setData({
            products: [...this.data.products, ...newProducts],
            page: this.data.page + 1,
            hasMore,
            loading: false
          })
        }
      },
      fail: (error) => {
        console.error('加载商品失败:', error)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
        this.setData({ loading: false })
      }
    })
  },

  navigateToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/distributor/products/detail/index?id=${id}`
    })
  }
}) 