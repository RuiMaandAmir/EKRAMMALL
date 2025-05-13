// 导入API服务
const { userApi } = require('../../../services/api');
import util from '../../../utils/util';

const app = getApp()

Page({
  data: {
    nickname: ''
  },

  onLoad: function() {
    this.loadUserInfo();
  },

  // 加载用户信息
  async loadUserInfo() {
    try {
      const userInfo = await userApi.getUserInfo();
      this.setData({
        nickname: userInfo.nickName || ''
      });
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  },

  // 输入框内容变化
  onInput(e) {
    this.setData({
      nickname: e.detail.value
    });
  },

  // 清空输入框
  clearInput() {
    this.setData({
      nickname: ''
    });
  },

  // 保存昵称
  async saveNickname() {
    const { nickname } = this.data;
    
    // 验证昵称
    if (!nickname) {
      util.showError('请输入昵称');
      return;
    }
    
    if (nickname.length < 2) {
      util.showError('昵称至少2个字符');
      return;
    }
    
    if (nickname.length > 20) {
      util.showError('昵称最多20个字符');
      return;
    }

    try {
      // 更新用户信息
      await userApi.updateUserInfo({ nickName: nickname });
      
      // 更新全局用户信息
      const pages = getCurrentPages();
      const prevPage = pages[pages.length - 2];
      if (prevPage) {
        prevPage.setData({
          'userInfo.nickName': nickname
        });
      }
      
      util.showSuccess('修改成功');
      
      // 返回上一页
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (error) {
      util.showError('修改失败');
    }
  }
}) 