// app.js
App({
  onLaunch: function () {
    // 检查登录状态
    this.checkLoginStatus();
    
    // 获取设备信息
    this.getSystemInfo();
  },
  
  checkLoginStatus: function () {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
      this.globalData.isLoggedIn = true;
    } else {
      this.globalData.isLoggedIn = false;
    }
  },
  
  getSystemInfo: function () {
    let that = this;
    wx.getSystemInfo({
      success: function (res) {
        that.globalData.systemInfo = res;
        
        // 设置导航栏高度
        that.globalData.navBarHeight = res.statusBarHeight + 44;
      }
    });
  },
  
  login: function (userInfo) {
    this.globalData.userInfo = userInfo;
    this.globalData.isLoggedIn = true;
    wx.setStorageSync('userInfo', userInfo);
  },
  
  logout: function () {
    this.globalData.userInfo = null;
    this.globalData.isLoggedIn = false;
    this.globalData.token = '';
    wx.removeStorageSync('userInfo');
    wx.removeStorageSync('token');
  },
  
  globalData: {
    userInfo: null,
    isLoggedIn: false,
    token: '',
    systemInfo: null,
    navBarHeight: 0,
    baseUrl: 'http://localhost:8000',
    apiUrl: 'http://localhost:8000/api'
  }
}) 