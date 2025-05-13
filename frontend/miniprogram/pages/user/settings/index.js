// 导入API服务
const { userApi } = require('../../../services/api');
import util from '../../../utils/util';

const app = getApp()

Page({
  data: {
    userInfo: null,
    settings: {
      notification: true
    },
    cacheSize: '0KB',
    version: '1.0.0'
  },

  onLoad: function() {
    this.loadUserInfo();
    this.loadSettings();
    this.calculateCacheSize();
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

  // 加载设置
  async loadSettings() {
    try {
      const settings = await userApi.getSettings();
      this.setData({ settings });
    } catch (error) {
      console.error('获取设置失败:', error);
    }
  },

  // 计算缓存大小
  calculateCacheSize() {
    wx.getStorageInfo({
      success: (res) => {
        const size = (res.currentSize / 1024).toFixed(2);
        this.setData({
          cacheSize: size + 'KB'
        });
      }
    });
  },

  // 修改头像
  changeAvatar() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        try {
          const tempFilePath = res.tempFilePaths[0];
          const avatarUrl = await userApi.uploadAvatar(tempFilePath);
          await userApi.updateUserInfo({ avatarUrl });
          this.setData({
            'userInfo.avatarUrl': avatarUrl
          });
          util.showSuccess('修改成功');
        } catch (error) {
          util.showError('修改失败');
        }
      }
    });
  },

  // 修改昵称
  changeNickname() {
    wx.navigateTo({
      url: '/pages/user/nickname/index'
    });
  },

  // 修改手机号
  changePhone() {
    wx.navigateTo({
      url: '/pages/user/phone/index'
    });
  },

  // 切换消息通知
  async toggleNotification(e) {
    try {
      const notification = e.detail.value;
      await userApi.updateSettings({ notification });
      this.setData({
        'settings.notification': notification
      });
      util.showSuccess('设置成功');
    } catch (error) {
      util.showError('设置失败');
    }
  },

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '提示',
      content: '确定要清除缓存吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorage({
            success: () => {
              this.calculateCacheSize();
              util.showSuccess('清除成功');
            }
          });
        }
      }
    });
  },

  // 检查更新
  checkUpdate() {
    const updateManager = wx.getUpdateManager();
    updateManager.onCheckForUpdate((res) => {
      if (res.hasUpdate) {
        wx.showModal({
          title: '更新提示',
          content: '新版本已经准备好，是否重启应用？',
          success: (res) => {
            if (res.confirm) {
              updateManager.applyUpdate();
            }
          }
        });
      } else {
        util.showSuccess('已是最新版本');
      }
    });
  },

  // 清除全部缓存
  clearAllCache() {
    wx.showModal({
      title: '提示',
      content: '确定要清除全部缓存吗？这将清除所有本地数据。',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorage({
            success: () => {
              this.calculateCacheSize();
              util.showSuccess('清除成功');
            }
          });
        }
      }
    });
  }
}) 