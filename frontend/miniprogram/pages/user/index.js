// 导入API服务
const { userApi, orderApi } = require('../../services/api');
import util from '../../utils/util';

const app = getApp()

Page({
  data: {
    userInfo: null,
    orderCounts: {
      unpaid: 0,
      unshipped: 0,
      shipped: 0
    }
  },

  onLoad: function() {
    this.loadUserInfo();
    this.loadOrderCounts();
  },

  onShow: function() {
    if (this.data.userInfo) {
      this.loadOrderCounts();
    }
  },

  // 加载用户信息
  async loadUserInfo() {
    try {
      const userInfo = await userApi.getUserInfo();
      this.setData({ userInfo });
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  },

  // 加载订单数量
  async loadOrderCounts() {
    try {
      const counts = await orderApi.getOrderCounts();
      this.setData({ orderCounts: counts });
    } catch (error) {
      console.error('获取订单数量失败:', error);
    }
  },

  // 查看全部订单
  viewAllOrders() {
    wx.navigateTo({
      url: '/pages/order/list/index'
    });
  },

  // 查看指定状态订单
  viewOrders(e) {
    const { status } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/order/list/index?status=${status}`
    });
  },

  // 跳转到设置页面
  goToSettings() {
    wx.navigateTo({
      url: '/pages/user/settings/index'
    });
  },

  // 跳转到地址管理
  goToAddress() {
    wx.navigateTo({
      url: '/pages/address/list/index'
    });
  },

  // 跳转到收藏
  goToFavorites() {
    wx.navigateTo({
      url: '/pages/user/favorites/index'
    });
  },

  // 跳转到优惠券
  goToCoupons() {
    wx.navigateTo({
      url: '/pages/user/coupons/index'
    });
  },

  // 跳转到积分商城
  goToPoints() {
    wx.navigateTo({
      url: '/pages/user/points/index'
    });
  },

  // 跳转到客服
  goToCustomerService() {
    wx.navigateTo({
      url: '/pages/user/service/index'
    });
  },

  // 跳转到关于我们
  goToAbout() {
    wx.navigateTo({
      url: '/pages/user/about/index'
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          userApi.logout();
          this.setData({ userInfo: null });
          wx.reLaunch({
            url: '/pages/index/index'
          });
        }
      }
    });
  }
}) 