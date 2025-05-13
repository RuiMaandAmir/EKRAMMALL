 // 导入API服务
const { productApi } = require('../../services/api');
import util from '../../utils/util';

Page({
  data: {
    // 分类数据
    categories: [],
    currentCategory: {},
    subcategories: [],
    
    // 商品数据
    products: [],
    page: 1,
    hasMore: true,
    
    // 状态
    loading: true,
    refreshing: false
  },

  onLoad: function(options) {
    // 如果有传入分类ID，则加载指定分类
    if (options.id) {
      this.loadCategoryById(options.id);
    } else {
      // 否则加载所有分类
      this.loadCategories();
    }
  },

  // 加载所有分类
  async loadCategories() {
    try {
      util.showLoading();
      const categories = await productApi.getCategories();
      
      this.setData({
        categories,
        currentCategory: categories[0] || {}
      });

      // 加载第一个分类的子分类和商品
      if (categories.length > 0) {
        await this.loadSubcategories(categories[0].id);
        await this.loadProducts(categories[0].id);
      }
    } catch (error) {
      util.showError('加载失败');
    } finally {
      util.hideLoading();
      this.setData({ loading: false });
    }
  },

  // 根据ID加载分类
  async loadCategoryById(id) {
    try {
      util.showLoading();
      const categories = await productApi.getCategories();
      const currentCategory = categories.find(c => c.id === parseInt(id)) || categories[0];
      
      this.setData({
        categories,
        currentCategory
      });

      await this.loadSubcategories(currentCategory.id);
      await this.loadProducts(currentCategory.id);
    } catch (error) {
      util.showError('加载失败');
    } finally {
      util.hideLoading();
      this.setData({ loading: false });
    }
  },

  // 加载子分类
  async loadSubcategories(categoryId) {
    try {
      const subcategories = await productApi.getSubcategories(categoryId);
      this.setData({ subcategories });
    } catch (error) {
      console.error('加载子分类失败:', error);
      this.setData({ subcategories: [] });
    }
  },

  // 加载商品列表
  async loadProducts(categoryId, page = 1) {
    try {
      const result = await productApi.getProducts({
        category_id: categoryId,
        page
      });

      this.setData({
        products: page === 1 ? result.items : [...this.data.products, ...result.items],
        hasMore: result.has_more,
        page
      });
    } catch (error) {
      console.error('加载商品失败:', error);
      this.setData({
        products: page === 1 ? [] : this.data.products,
        hasMore: false
      });
    }
  },

  // 切换分类
  async onCategoryTap(e) {
    const { id } = e.currentTarget.dataset;
    const category = this.data.categories.find(c => c.id === parseInt(id));
    
    if (category && category.id !== this.data.currentCategory.id) {
      this.setData({
        currentCategory: category,
        products: [],
        page: 1,
        hasMore: true
      });

      await this.loadSubcategories(category.id);
      await this.loadProducts(category.id);
    }
  },

  // 点击子分类
  onSubcategoryTap(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/category/list?id=${id}`
    });
  },

  // 点击商品
  onProductTap(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/product/detail/index?id=${id}`
    });
  },

  // 下拉刷新
  async onRefresh() {
    this.setData({
      refreshing: true,
      page: 1,
      hasMore: true
    });

    await this.loadSubcategories(this.data.currentCategory.id);
    await this.loadProducts(this.data.currentCategory.id);

    this.setData({ refreshing: false });
  },

  // 加载更多
  async onLoadMore() {
    if (this.data.hasMore && !this.data.loading) {
      const nextPage = this.data.page + 1;
      await this.loadProducts(this.data.currentCategory.id, nextPage);
    }
  },

  // 分享
  onShareAppMessage: function() {
    return {
      title: `${this.data.currentCategory.name} - 伊客拉穆商城`,
      path: `/pages/category/index?id=${this.data.currentCategory.id}`
    };
  }
});