// 导入API服务
const { cartApi } = require('../../services/api');
import util from '../../utils/util';

Page({
  data: {
    cartItems: [],
    allSelected: false,
    totalPrice: 0,
    selectedCount: 0
  },

  onLoad: function() {
    this.loadCartItems();
  },

  onShow: function() {
    // 每次显示页面时重新加载购物车数据
    this.loadCartItems();
  },

  // 加载购物车数据
  async loadCartItems() {
    try {
      util.showLoading();
      const cartItems = await cartApi.getCartItems();
      
      // 为每个商品添加选中状态
      const itemsWithSelection = cartItems.map(item => ({
        ...item,
        selected: false
      }));
      
      this.setData({
        cartItems: itemsWithSelection,
        allSelected: false,
        totalPrice: 0,
        selectedCount: 0
      });
    } catch (error) {
      util.showError('加载失败');
    } finally {
      util.hideLoading();
    }
  },

  // 选择/取消选择商品
  onItemSelect(e) {
    const { id } = e.currentTarget.dataset;
    const { cartItems } = this.data;
    
    const updatedItems = cartItems.map(item => {
      if (item.id === id) {
        return { ...item, selected: !item.selected };
      }
      return item;
    });
    
    this.updateCartState(updatedItems);
  },

  // 全选/取消全选
  onSelectAll() {
    const { cartItems, allSelected } = this.data;
    
    const updatedItems = cartItems.map(item => ({
      ...item,
      selected: !allSelected
    }));
    
    this.updateCartState(updatedItems);
  },

  // 更新购物车状态
  updateCartState(items) {
    const allSelected = items.length > 0 && items.every(item => item.selected);
    const selectedCount = items.filter(item => item.selected).length;
    const totalPrice = items.reduce((total, item) => {
      if (item.selected) {
        return total + item.price * item.quantity;
      }
      return total;
    }, 0);
    
    this.setData({
      cartItems: items,
      allSelected,
      selectedCount,
      totalPrice: totalPrice.toFixed(2)
    });
  },

  // 修改商品数量
  async onQuantityChange(e) {
    const { id, type } = e.currentTarget.dataset;
    const { cartItems } = this.data;
    
    const item = cartItems.find(item => item.id === id);
    if (!item) return;
    
    let quantity = item.quantity;
    if (type === 'minus' && quantity > 1) {
      quantity--;
    } else if (type === 'plus' && quantity < 99) {
      quantity++;
    }
    
    try {
      await cartApi.updateCartItem(id, { quantity });
      
      const updatedItems = cartItems.map(item => {
        if (item.id === id) {
          return { ...item, quantity };
        }
        return item;
      });
      
      this.updateCartState(updatedItems);
    } catch (error) {
      util.showError('修改失败');
    }
  },

  // 输入商品数量
  async onQuantityInput(e) {
    const { id } = e.currentTarget.dataset;
    let quantity = parseInt(e.detail.value) || 1;
    quantity = Math.min(Math.max(quantity, 1), 99);
    
    try {
      await cartApi.updateCartItem(id, { quantity });
      
      const { cartItems } = this.data;
      const updatedItems = cartItems.map(item => {
        if (item.id === id) {
          return { ...item, quantity };
        }
        return item;
      });
      
      this.updateCartState(updatedItems);
    } catch (error) {
      util.showError('修改失败');
    }
  },

  // 去结算
  onSettlement() {
    const { cartItems } = this.data;
    const selectedItems = cartItems.filter(item => item.selected);
    
    if (selectedItems.length === 0) {
      util.showError('请选择商品');
      return;
    }
    
    // 将选中的商品信息存储到本地
    wx.setStorageSync('temp_order', selectedItems);
    
    // 跳转到订单确认页
    wx.navigateTo({
      url: '/pages/order/confirm/index'
    });
  },

  // 去购物
  onGoShopping() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
}); 