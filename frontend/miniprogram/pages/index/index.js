// 导入API服务
const { 
  productApi, 
  promotionApi, 
  dashboardApi 
} = require('../../services/api');

import util from '../../utils/util'

const app = getApp()

Page({
  data: {
    // 页面数据
    banners: [],
    navItems: [],
    flashSaleProducts: [],
    featuredProducts: [],
    categoryProducts: [],
    categories: [],
    
    // 状态管理
    loading: true,
    showBackToTop: false,
    
    // 倒计时
    countdownTime: {
      hours: '00',
      minutes: '00',
      seconds: '00'
    },
    
    // 系统信息
    statusBarHeight: getApp().globalData.statusBarHeight || 20,
    navBarHeight: getApp().globalData.navBarHeight || 44,
    flashSaleEndTime: 0,
    scrollTop: 0,
    recommendProducts: [],
    newProducts: [],
    flashSaleTime: '',
    hasMore: true,
    page: 1,
    showAd: false,
    adData: null
  },

  onLoad: function() {
    // 记录页面访问
    dashboardApi.recordPageView('home');
    
    // 加载数据
    this.loadInitialData();
    
    // 初始化倒计时
    this.initCountdown();

    const app = getApp();
    if (app.globalData.currentAd) {
      this.setData({
        showAd: true,
        adData: app.globalData.currentAd
      });
    }
  },
  
  onShow: function() {
    // 如果购物车有更新，可能需要重新加载某些数据
    if (getApp().globalData.cartUpdated) {
      // 重新加载相关数据
      getApp().globalData.cartUpdated = false;
      this.updateCartBadge();
    }
  },
  
  onUnload: function() {
    // 清除定时器
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  },
  
  onPageScroll: function(e) {
    // 更新滚动位置
    const scrollTop = e.scrollTop;
    // 显示/隐藏回到顶部按钮
    const showBackToTop = scrollTop > 300;
    
    if (showBackToTop !== this.data.showBackToTop) {
      this.setData({
        showBackToTop
      });
    }
  },
  
  // 获取首页数据
  async loadInitialData() {
    try {
      util.showLoading()
      const [banners, categories, flashSale, recommend, newProducts] = await Promise.all([
        this.loadBanners(),
        this.loadCategories(),
        this.loadFlashSale(),
        this.loadRecommendProducts(),
        this.loadNewProducts()
      ])

      this.setData({
        banners,
        categories,
        flashSaleProducts: flashSale.products,
        flashSaleTime: flashSale.time,
        recommendProducts: recommend.products,
        newProducts: newProducts.products
      })
    } catch (error) {
      util.showError('加载失败')
    } finally {
      util.hideLoading()
      wx.stopPullDownRefresh()
    }
  },
  
  // 加载轮播图
  async loadBanners() {
    // TODO: 实现轮播图加载
    return [
      {
        id: 1,
        image: '/images/banners/banner1.jpg'
      },
      {
        id: 2,
        image: '/images/banners/banner2.jpg'
      }
    ]
  },
  
  // 加载分类
  async loadCategories() {
    try {
      const categories = await productApi.getCategories()
      return categories.map(category => ({
        id: category.id,
        name: category.name,
        icon: category.icon
      }))
    } catch (error) {
      return []
    }
  },
  
  // 加载限时特惠
  async loadFlashSale() {
    // TODO: 实现限时特惠加载
    return {
      products: [
        {
          id: 1,
          name: '清真牛肉干',
          image: '/images/products/beef.jpg',
          price: '39.9'
        }
      ],
      time: '12:00:00'
    }
  },
  
  // 加载推荐商品
  async loadRecommendProducts() {
    try {
      const products = await productApi.getProducts({
        page: this.data.page,
        recommend: true
      })
      return {
        products: products.items,
        hasMore: products.has_more
      }
    } catch (error) {
      return {
        products: [],
        hasMore: false
      }
    }
  },
  
  // 加载新品
  async loadNewProducts() {
    try {
      const products = await productApi.getProducts({
        page: this.data.page,
        new: true
      })
      return {
        products: products.items,
        hasMore: products.has_more
      }
    } catch (error) {
      return {
        products: [],
        hasMore: false
      }
    }
  },
  
  // 加载更多商品
  async loadMoreProducts() {
    if (this.data.loading) return

    this.setData({ loading: true })
    try {
      const [recommend, newProducts] = await Promise.all([
        this.loadRecommendProducts(),
        this.loadNewProducts()
      ])

      this.setData({
        recommendProducts: [...this.data.recommendProducts, ...recommend.products],
        newProducts: [...this.data.newProducts, ...newProducts.products],
        hasMore: recommend.hasMore || newProducts.hasMore,
        page: this.data.page + 1
      })
    } catch (error) {
      util.showError('加载失败')
    } finally {
      this.setData({ loading: false })
    }
  },
  
  // 点击搜索跳转
  onSearchTap() {
    wx.navigateTo({
      url: '/pages/search/index'
    })
  },
  
  // 点击banner
  onBannerTap(e) {
    const { id } = e.currentTarget.dataset
    // TODO: 处理轮播图点击
  },
  
  // 点击导航菜单项
  onTapNavItem: function(e) {
    const { url } = e.currentTarget.dataset;
    wx.navigateTo({
      url
    });
  },
  
  // 查看更多限时抢购商品
  viewMoreFlashSale: function() {
    wx.navigateTo({
      url: '/pages/activity/flash'
    });
  },
  
  // 查看更多推荐商品
  viewMoreFeatured: function() {
    wx.navigateTo({
      url: '/pages/category/list?type=featured'
    });
  },
  
  // 查看更多分类商品
  viewMoreCategory: function(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/category/list?id=${id}`
    });
  },
  
  // 查看商品详情
  viewProductDetail: function(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/product/detail?id=${id}`
    });
  },
  
  // 返回顶部
  backToTop: function() {
    wx.pageScrollTo({
      scrollTop: 0,
      duration: 300
    });
  },
  
  // 下拉刷新
  onPullDownRefresh: function() {
    this.setData({
      page: 1,
      hasMore: true
    })
    this.loadInitialData()
  },
  
  // 上拉加载更多
  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMoreProducts()
    }
  },
  
  // 分享
  onShareAppMessage: function() {
    return {
      title: '伊客拉穆商城 - 品质购物新选择',
      path: '/pages/index/index',
      imageUrl: '/assets/images/share-home.jpg' // 分享图片
    };
  },
  
  // 更新购物车角标
  updateCartBadge: function() {
    // 模拟从缓存获取购物车数量
    const cartItems = wx.getStorageSync('cart_items') || [];
    const cartCount = cartItems.length;
    
    if (cartCount > 0) {
      wx.setTabBarBadge({
        index: 2, // 购物车的tabBar索引
        text: cartCount.toString()
      }).catch(err => {
        // 忽略tabBar还未准备好的错误
        console.log('setTabBarBadge error:', err);
      });
    } else {
      wx.removeTabBarBadge({
        index: 2
      }).catch(err => {
        // 忽略tabBar还未准备好的错误
        console.log('removeTabBarBadge error:', err);
      });
    }
  },
  
  // 初始化倒计时
  initCountdown: function() {
    // 更新倒计时
    this.updateCountdown();
    // 每秒更新一次倒计时
    this.countdownTimer = setInterval(() => {
      this.updateCountdown();
    }, 1000);
  },
  
  // 更新倒计时
  updateCountdown: function() {
    if (!this.data.flashSaleEndTime) return;
    
    const now = new Date().getTime();
    const endTime = this.data.flashSaleEndTime;
    let remainTime = Math.max(0, endTime - now);
    
    if (remainTime <= 0) {
      // 倒计时结束
      clearInterval(this.countdownTimer);
      this.setData({
        countdownTime: {
          hours: '00',
          minutes: '00',
          seconds: '00'
        }
      });
      return;
    }
    
    // 计算剩余时间
    const hours = Math.floor(remainTime / (1000 * 60 * 60));
    remainTime -= hours * (1000 * 60 * 60);
    const minutes = Math.floor(remainTime / (1000 * 60));
    remainTime -= minutes * (1000 * 60);
    const seconds = Math.floor(remainTime / 1000);
    
    this.setData({
      countdownTime: {
        hours: hours < 10 ? '0' + hours : hours.toString(),
        minutes: minutes < 10 ? '0' + minutes : minutes.toString(),
        seconds: seconds < 10 ? '0' + seconds : seconds.toString()
      }
    });
  },
  
  // 分类点击
  onCategoryTap(e) {
    const { id } = e.currentTarget.dataset
    wx.switchTab({
      url: `/pages/category/index?id=${id}`
    })
  },
  
  // 商品点击
  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product/detail/index?id=${id}`
    })
  },

  onAdClose() {
    this.setData({
      showAd: false
    });
  }
}); 