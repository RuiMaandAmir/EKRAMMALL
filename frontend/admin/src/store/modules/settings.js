// 不再从variables.scss导入
// import variables from '@/styles/variables.scss';

const state = {
  theme: '#4caf50', // 直接使用硬编码的颜色值
  showSettings: true,
  tagsView: true,
  fixedHeader: true,
  sidebarLogo: true,
  title: '伊客拉穆商城后台管理系统',
  shortTitle: '伊客拉穆'
};

const mutations = {
  CHANGE_SETTING: (state, { key, value }) => {
    // eslint-disable-next-line no-prototype-builtins
    if (state.hasOwnProperty(key)) {
      state[key] = value;
    }
  }
};

const actions = {
  changeSetting({ commit }, data) {
    commit('CHANGE_SETTING', data);
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions
}; 