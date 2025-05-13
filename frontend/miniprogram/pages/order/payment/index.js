// 导入API服务
const { orderApi } = require('../../../services/api');
import util from '../../../utils/util';

Page({
  data: {
    orderId: '',
    amount: '0.00',
    paymentMethods: [
      {
        id: 'wxpay',
        name: '微信支付',
        icon: '/images/icons/wxpay.png'
      },
      {
        id: 'alipay',
        name: '支付宝支付',
        icon: '/images/icons/alipay.png'
      }
    ],
    selectedPayment: '',
    countdown: 900, // 15分钟支付时限
    countdownText: '',
    showResult: false,
    paySuccess: false
  },

  onLoad: function(options) {
    const { orderId, amount } = options;
    if (!orderId || !amount) {
      util.showError('订单信息不完整');
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
      return;
    }

    this.setData({
      orderId,
      amount
    });

    // 开始倒计时
    this.startCountdown();
  },

  onUnload: function() {
    // 清除定时器
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  },

  // 选择支付方式
  onSelectPayment(e) {
    const { id } = e.currentTarget.dataset;
    this.setData({
      selectedPayment: id
    });
  },

  // 开始倒计时
  startCountdown() {
    this.countdownTimer = setInterval(() => {
      let { countdown } = this.data;
      if (countdown <= 0) {
        clearInterval(this.countdownTimer);
        this.setData({
          showResult: true,
          paySuccess: false
        });
        return;
      }

      countdown--;
      const minutes = Math.floor(countdown / 60);
      const seconds = countdown % 60;
      const countdownText = `${minutes}:${seconds.toString().padStart(2, '0')}`;

      this.setData({
        countdown,
        countdownText
      });
    }, 1000);
  },

  // 发起支付
  async onPay() {
    const { orderId, selectedPayment, amount } = this.data;

    if (!selectedPayment) {
      util.showError('请选择支付方式');
      return;
    }

    try {
      util.showLoading('支付中...');

      // 调用支付接口
      const payParams = await orderApi.createPayment({
        orderId,
        paymentMethod: selectedPayment,
        amount: parseFloat(amount)
      });

      // 发起微信支付
      if (selectedPayment === 'wxpay') {
        await this.wxPay(payParams);
      } else {
        // 支付宝支付
        await this.aliPay(payParams);
      }

      // 支付成功后更新订单状态
      await orderApi.updateOrderStatus(orderId, 'paid');

      this.setData({
        showResult: true,
        paySuccess: true
      });

      util.hideLoading();
    } catch (error) {
      util.hideLoading();
      util.showError('支付失败');
      this.setData({
        showResult: true,
        paySuccess: false
      });
    }
  },

  // 微信支付
  wxPay(payParams) {
    return new Promise((resolve, reject) => {
      wx.requestPayment({
        ...payParams,
        success: resolve,
        fail: reject
      });
    });
  },

  // 支付宝支付
  aliPay(payParams) {
    // 实现支付宝支付逻辑
    return Promise.resolve();
  },

  // 查看订单
  onViewOrder() {
    wx.redirectTo({
      url: `/pages/order/detail/index?id=${this.data.orderId}`
    });
  },

  // 重新支付
  onRetry() {
    this.setData({
      showResult: false,
      paySuccess: false
    });
  },

  // 返回首页
  onBackHome() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
}); 