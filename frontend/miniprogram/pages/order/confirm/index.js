// 导入API服务
const { orderApi, addressApi } = require('../../../services/api');
import util from '../../../utils/util';

Page({
  data: {
    address: null,
    orderItems: [],
    deliveryType: 'express',
    deliveryFee: 0,
    totalPrice: 0,
    actualPrice: 0,
    remark: ''
  },

  onLoad: function() {
    // 从本地存储获取购物车选中的商品
    const orderItems = wx.getStorageSync('temp_order');
    if (!orderItems || orderItems.length === 0) {
      util.showError('订单信息不存在');
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
      return;
    }

    // 计算商品总价
    const totalPrice = orderItems.reduce((total, item) => {
      return total + item.price * item.quantity;
    }, 0);

    this.setData({
      orderItems,
      totalPrice: totalPrice.toFixed(2),
      actualPrice: totalPrice.toFixed(2)
    });

    // 获取默认收货地址
    this.loadDefaultAddress();
  },

  // 加载默认收货地址
  async loadDefaultAddress() {
    try {
      const address = await addressApi.getDefaultAddress();
      if (address) {
        this.setData({ address });
      }
    } catch (error) {
      console.error('获取默认地址失败:', error);
    }
  },

  // 选择收货地址
  onSelectAddress() {
    wx.navigateTo({
      url: '/pages/address/list/index?select=true'
    });
  },

  // 选择配送方式
  onSelectDelivery(e) {
    const { type } = e.currentTarget.dataset;
    const deliveryFee = type === 'express' ? 10 : 0;
    const actualPrice = (parseFloat(this.data.totalPrice) + deliveryFee).toFixed(2);
    
    this.setData({
      deliveryType: type,
      deliveryFee: deliveryFee.toFixed(2),
      actualPrice
    });
  },

  // 输入订单备注
  onRemarkInput(e) {
    this.setData({
      remark: e.detail.value
    });
  },

  // 提交订单
  async onSubmitOrder() {
    const { address, orderItems, deliveryType, deliveryFee, totalPrice, actualPrice, remark } = this.data;

    if (!address) {
      util.showError('请选择收货地址');
      return;
    }

    try {
      util.showLoading('提交中...');

      // 构建订单数据
      const orderData = {
        addressId: address.id,
        items: orderItems.map(item => ({
          productId: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        deliveryType,
        deliveryFee: parseFloat(deliveryFee),
        totalPrice: parseFloat(totalPrice),
        actualPrice: parseFloat(actualPrice),
        remark
      };

      // 提交订单
      const orderId = await orderApi.createOrder(orderData);

      // 清除购物车中已下单的商品
      await this.clearOrderedItems();

      // 清除临时订单数据
      wx.removeStorageSync('temp_order');

      util.hideLoading();

      // 跳转到支付页面
      wx.navigateTo({
        url: `/pages/order/payment/index?orderId=${orderId}&amount=${actualPrice}`
      });
    } catch (error) {
      util.hideLoading();
      util.showError('提交订单失败');
    }
  },

  // 清除已下单的商品
  async clearOrderedItems() {
    const { orderItems } = this.data;
    const itemIds = orderItems.map(item => item.id);
    
    try {
      await orderApi.clearCartItems(itemIds);
    } catch (error) {
      console.error('清除购物车商品失败:', error);
    }
  }
}); 