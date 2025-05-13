// 导入API服务
const { productApi, cartApi } = require('../../../services/api');
import util from '../../../utils/util';

const app = getApp()

Page({
  data: {
    product: null,
    selectedSpec: null,
    quantity: 1,
    loading: true,
    error: null
  },

  onLoad: function(options) {
    if (options.id) {
      this.loadProductDetail(options.id)
    }
  },

  // 加载商品详情
  async loadProductDetail(id) {
    try {
      util.showLoading();
      const product = await productApi.getProductDetail(id);
      
      this.setData({
        product,
        selectedSpec: product.specs[0]?.id || null,
        loading: false
      });
    } catch (error) {
      util.showError('加载失败');
    } finally {
      util.hideLoading();
    }
  },

  // 选择规格
  onSpecSelect(e) {
    const { id } = e.currentTarget.dataset;
    this.setData({ selectedSpec: id });
  },

  // 修改数量
  onQuantityChange(e) {
    const { type } = e.currentTarget.dataset;
    let { quantity } = this.data;
    
    if (type === 'minus' && quantity > 1) {
      quantity--;
    } else if (type === 'plus' && quantity < 99) {
      quantity++;
    }
    
    this.setData({ quantity });
  },

  // 输入数量
  onQuantityInput(e) {
    let quantity = parseInt(e.detail.value) || 1;
    quantity = Math.min(Math.max(quantity, 1), 99);
    this.setData({ quantity });
  },

  // 加入购物车
  async onAddToCart() {
    if (!this.data.selectedSpec) {
      util.showError('请选择规格');
      return;
    }

    try {
      util.showLoading();
      await cartApi.addToCart({
        product_id: this.data.product.id,
        spec_id: this.data.selectedSpec,
        quantity: this.data.quantity
      });

      util.showSuccess('已加入购物车');
      
      // 更新购物车角标
      this.updateCartBadge();
    } catch (error) {
      util.showError('添加失败');
    } finally {
      util.hideLoading();
    }
  },

  // 立即购买
  onBuyNow() {
    if (!this.data.selectedSpec) {
      util.showError('请选择规格');
      return;
    }

    // 将商品信息存储到本地
    const orderInfo = {
      product_id: this.data.product.id,
      spec_id: this.data.selectedSpec,
      quantity: this.data.quantity
    };
    wx.setStorageSync('temp_order', orderInfo);

    // 跳转到订单确认页
    wx.navigateTo({
      url: '/pages/order/confirm/index'
    });
  },

  // 分享
  onShare() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
  },

  // 分享给朋友
  onShareAppMessage() {
    const { product } = this.data;
    return {
      title: product.name,
      path: `/pages/product/detail/index?id=${product.id}`,
      imageUrl: product.images[0]
    };
  },

  // 分享到朋友圈
  onShareTimeline() {
    const { product } = this.data;
    return {
      title: product.name,
      query: `id=${product.id}`,
      imageUrl: product.images[0]
    };
  },

  // 更新购物车角标
  async updateCartBadge() {
    try {
      const cartCount = await cartApi.getCartCount();
      if (cartCount > 0) {
        wx.setTabBarBadge({
          index: 2,
          text: cartCount.toString()
        });
      } else {
        wx.removeTabBarBadge({
          index: 2
        });
      }
    } catch (error) {
      console.error('更新购物车角标失败:', error);
    }
  }
}) 