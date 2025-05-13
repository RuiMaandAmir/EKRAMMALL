// 导入API服务
const { orderApi } = require('../../../services/api');
import util from '../../../utils/util';

const app = getApp()

Page({
  data: {
    currentTab: 'all',
    orders: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad: function() {
    this.loadOrders();
  },

  onShow: function() {
    // 每次显示页面时重新加载订单数据
    this.setData({
      page: 1,
      orders: [],
      hasMore: true
    });
    this.loadOrders();
  },

  onPullDownRefresh: function() {
    this.setData({
      page: 1,
      orders: [],
      hasMore: true
    });
    this.loadOrders().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore();
    }
  },

  // 切换标签页
  onTabChange(e) {
    const { tab } = e.currentTarget.dataset;
    this.setData({
      currentTab: tab,
      page: 1,
      orders: [],
      hasMore: true
    });
    this.loadOrders();
  },

  // 加载订单列表
  async loadOrders() {
    if (this.data.loading) return;

    try {
      this.setData({ loading: true });

      const { currentTab, page, pageSize } = this.data;
      const orders = await orderApi.getOrders({
        status: currentTab === 'all' ? '' : currentTab,
        page,
        pageSize
      });

      // 处理订单数据
      const formattedOrders = orders.map(order => ({
        ...order,
        statusText: this.getStatusText(order.status),
        totalQuantity: order.products.reduce((total, product) => total + product.quantity, 0)
      }));

      this.setData({
        orders: page === 1 ? formattedOrders : [...this.data.orders, ...formattedOrders],
        hasMore: formattedOrders.length === pageSize
      });
    } catch (error) {
      util.showError('加载失败');
    } finally {
      this.setData({ loading: false });
    }
  },

  // 加载更多
  loadMore() {
    this.setData({
      page: this.data.page + 1
    });
    this.loadOrders();
  },

  // 获取订单状态文本
  getStatusText(status) {
    const statusMap = {
      unpaid: '待付款',
      unshipped: '待发货',
      shipped: '待收货',
      completed: '已完成',
      cancelled: '已取消'
    };
    return statusMap[status] || status;
  },

  // 点击订单
  onOrderTap(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/order/detail/index?id=${id}`
    });
  },

  // 取消订单
  async onCancelOrder(e) {
    const { id } = e.currentTarget.dataset;
    
    try {
      await util.showModal('提示', '确定要取消该订单吗？');
      util.showLoading('取消中...');
      
      await orderApi.cancelOrder(id);
      
      // 更新订单状态
      const orders = this.data.orders.map(order => {
        if (order.id === id) {
          return {
            ...order,
            status: 'cancelled',
            statusText: '已取消'
          };
        }
        return order;
      });
      
      this.setData({ orders });
      util.showSuccess('取消成功');
    } catch (error) {
      if (error.errMsg !== 'showModal:cancel') {
        util.showError('取消失败');
      }
    } finally {
      util.hideLoading();
    }
  },

  // 支付订单
  onPayOrder(e) {
    const { id } = e.currentTarget.dataset;
    const order = this.data.orders.find(order => order.id === id);
    if (!order) return;

    wx.navigateTo({
      url: `/pages/order/payment/index?orderId=${id}&amount=${order.totalPrice}`
    });
  },

  // 确认收货
  async onConfirmReceive(e) {
    const { id } = e.currentTarget.dataset;
    
    try {
      await util.showModal('提示', '确认已收到商品？');
      util.showLoading('确认中...');
      
      await orderApi.confirmReceive(id);
      
      // 更新订单状态
      const orders = this.data.orders.map(order => {
        if (order.id === id) {
          return {
            ...order,
            status: 'completed',
            statusText: '已完成'
          };
        }
        return order;
      });
      
      this.setData({ orders });
      util.showSuccess('确认成功');
    } catch (error) {
      if (error.errMsg !== 'showModal:cancel') {
        util.showError('确认失败');
      }
    } finally {
      util.hideLoading();
    }
  },

  // 删除订单
  async onDeleteOrder(e) {
    const { id } = e.currentTarget.dataset;
    
    try {
      await util.showModal('提示', '确定要删除该订单吗？');
      util.showLoading('删除中...');
      
      await orderApi.deleteOrder(id);
      
      // 从列表中移除订单
      const orders = this.data.orders.filter(order => order.id !== id);
      this.setData({ orders });
      
      util.showSuccess('删除成功');
    } catch (error) {
      if (error.errMsg !== 'showModal:cancel') {
        util.showError('删除失败');
      }
    } finally {
      util.hideLoading();
    }
  },

  // 再次购买
  async onBuyAgain(e) {
    const { id } = e.currentTarget.dataset;
    const order = this.data.orders.find(order => order.id === id);
    if (!order) return;

    try {
      util.showLoading('处理中...');
      
      // 将商品添加到购物车
      await orderApi.addToCartFromOrder(id);
      
      util.hideLoading();
      
      // 跳转到购物车页面
      wx.switchTab({
        url: '/pages/cart/index'
      });
    } catch (error) {
      util.hideLoading();
      util.showError('操作失败');
    }
  },

  // 去购物
  onGoShopping() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
}) 