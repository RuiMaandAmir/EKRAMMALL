// 导入API服务
const { 
  productApi, 
  promotionApi, 
  dashboardApi 
} = require('../../services/api');

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
    scrollTop: 0
  },

  onLoad: function() {
    // 记录页面访问
    dashboardApi.recordPageView('home');
    
    // 加载数据
    this.fetchHomeData();
    
    // 初始化倒计时
    this.initCountdown();
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
  fetchHomeData: function() {
    // 显示加载状态
    this.setData({
      loading: true
    });

    // 模拟API请求
    setTimeout(() => {
      // 模拟轮播图数据
      const banners = [
        { id: 1, imageUrl: '/images/banner1.jpg', linkUrl: '/pages/product/detail?id=1' },
        { id: 2, imageUrl: '/images/banner2.jpg', linkUrl: '/pages/category/list?id=2' },
        { id: 3, imageUrl: '/images/banner3.jpg', linkUrl: '/pages/activity/detail?id=1' }
      ];

      // 模拟导航菜单数据
      const navItems = [
        { id: 1, name: '新品上市', icon: '/images/nav_new.png', url: '/pages/category/list?type=new' },
        { id: 2, name: '热卖商品', icon: '/images/nav_hot.png', url: '/pages/category/list?type=hot' },
        { id: 3, name: '优惠活动', icon: '/images/nav_sale.png', url: '/pages/activity/list' },
        { id: 4, name: '精选推荐', icon: '/images/nav_featured.png', url: '/pages/category/list?type=featured' },
        { id: 5, name: '品牌专区', icon: '/images/nav_brand.png', url: '/pages/brand/list' },
        { id: 6, name: '会员中心', icon: '/images/nav_member.png', url: '/pages/user/member' },
        { id: 7, name: '每日签到', icon: '/images/nav_checkin.png', url: '/pages/activity/checkin' },
        { id: 8, name: '积分商城', icon: '/images/nav_points.png', url: '/pages/points/mall' },
        { id: 9, name: '拼团活动', icon: '/images/nav_group.png', url: '/pages/group/list' },
        { id: 10, name: '全部分类', icon: '/images/nav_category.png', url: '/pages/category/index' }
      ];

      // 模拟限时抢购数据
      const flashSaleProducts = this.generateMockProducts(10, 'flash');

      // 模拟精选商品数据
      const featuredProducts = this.generateMockProducts(6, 'featured');

      // 模拟分类商品数据
      const categoryProducts = [
        {
          id: 1,
          name: '时尚服饰',
          products: this.generateMockProducts(4, 'fashion')
        },
        {
          id: 2,
          name: '电子数码',
          products: this.generateMockProducts(4, 'digital')
        },
        {
          id: 3,
          name: '家居生活',
          products: this.generateMockProducts(4, 'home')
        }
      ];

      // 设置限时抢购结束时间为24小时后
      const endTime = new Date();
      endTime.setHours(endTime.getHours() + 24);

      this.setData({
        loading: false,
        banners,
        navItems,
        flashSaleProducts,
        featuredProducts,
        categoryProducts,
        flashSaleEndTime: endTime.getTime()
      });

      // 启动倒计时
      this.startCountdown();
    }, 1500);
  },
  
  // 生成模拟商品数据
  generateMockProducts: function(count, type) {
    const products = [];
    const typeConfig = {
      flash: { priceRange: [9.9, 99.9], discountRange: [0.3, 0.8] },
      featured: { priceRange: [39.9, 299.9], discountRange: [0.5, 0.9] },
      fashion: { priceRange: [59.9, 399.9], discountRange: [0.6, 0.95] },
      digital: { priceRange: [99.9, 2999.9], discountRange: [0.7, 0.95] },
      home: { priceRange: [29.9, 599.9], discountRange: [0.5, 0.9] }
    };
    
    const config = typeConfig[type] || typeConfig.featured;
    
    for (let i = 1; i <= count; i++) {
      const originalPrice = (Math.random() * (config.priceRange[1] - config.priceRange[0]) + config.priceRange[0]).toFixed(2);
      const discountRate = Math.random() * (config.discountRange[1] - config.discountRange[0]) + config.discountRange[0];
      const price = (originalPrice * discountRate).toFixed(2);
      
      products.push({
        id: `${type}_${i}`,
        name: `${this.getProductNamePrefix(type)}商品${i}`,
        image: `/images/${type}_${i}.jpg`,
        price: parseFloat(price),
        originalPrice: parseFloat(originalPrice),
        sales: Math.floor(Math.random() * 1000) + 50
      });
    }
    
    return products;
  },
  
  // 根据商品类型获取名称前缀
  getProductNamePrefix: function(type) {
    const prefixes = {
      flash: '限时抢购',
      featured: '精选推荐',
      fashion: '时尚',
      digital: '数码',
      home: '家居'
    };
    return prefixes[type] || '热门';
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
  
  // 点击搜索跳转
  onTapSearch: function() {
    wx.navigateTo({
      url: '/pages/search/index'
    });
  },
  
  // 点击banner
  onTapBanner: function(e) {
    const { url } = e.currentTarget.dataset;
    if (url) {
      // 判断链接类型并跳转
      if (url.startsWith('http')) {
        // 网页链接，使用web-view打开
        wx.navigateTo({
          url: `/pages/webview/index?url=${encodeURIComponent(url)}`
        });
      } else {
        // 小程序内部链接，直接跳转
        wx.navigateTo({
          url
        });
      }
    }
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
    // 重新加载数据
    this.fetchHomeData();
    // 完成刷新
    wx.stopPullDownRefresh();
  },
  
  // 上拉加载更多
  onReachBottom: function() {
    // 首页不需要实现加载更多
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
  }
}); 