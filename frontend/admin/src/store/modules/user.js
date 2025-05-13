import { login, logout, getInfo } from '@/api/user';
import { getToken, setToken, removeToken } from '@/utils/auth';
import router, { resetRouter } from '@/router';

const state = {
  token: getToken(),
  name: '',
  avatar: '',
  introduction: '',
  roles: [],
  permissions: []
};

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token;
  },
  SET_INTRODUCTION: (state, introduction) => {
    state.introduction = introduction;
  },
  SET_NAME: (state, name) => {
    state.name = name;
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar;
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles;
  },
  SET_PERMISSIONS: (state, permissions) => {
    state.permissions = permissions;
  }
};

const actions = {
  // 用户登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo;
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password })
        .then(response => {
          const { data } = response;
          commit('SET_TOKEN', data.token);
          setToken(data.token);
          resolve();
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  // 获取用户信息
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo()
        .then(response => {
          const { data } = response;

          if (!data) {
            reject('验证失败，请重新登录。');
          }

          const { roles, name, avatar, introduction, permissions } = data;

          // 角色必须是非空数组
          if (!roles || roles.length <= 0) {
            reject('用户角色不能为空！');
          }

          commit('SET_ROLES', roles);
          commit('SET_NAME', name);
          commit('SET_AVATAR', avatar);
          commit('SET_INTRODUCTION', introduction);
          commit('SET_PERMISSIONS', permissions);
          resolve(data);
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  // 用户登出
  logout({ commit, state, dispatch }) {
    return new Promise((resolve, reject) => {
      logout()
        .then(() => {
          commit('SET_TOKEN', '');
          commit('SET_ROLES', []);
          commit('SET_PERMISSIONS', []);
          removeToken();
          resetRouter();
          
          // 重置访问的视图和缓存的视图
          dispatch('tagsView/delAllViews', null, { root: true });

          resolve();
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  // 重置令牌
  resetToken({ commit }) {
    return new Promise(resolve => {
      commit('SET_TOKEN', '');
      commit('SET_ROLES', []);
      commit('SET_PERMISSIONS', []);
      removeToken();
      resolve();
    });
  },

  // 动态修改权限
  async changeRoles({ commit, dispatch }, role) {
    const token = role + '-token';

    commit('SET_TOKEN', token);
    setToken(token);

    const { roles } = await dispatch('getInfo');

    resetRouter();

    // 基于角色生成可访问路由
    const accessRoutes = await dispatch('permission/generateRoutes', roles, { root: true });
    
    // 动态添加可访问路由
    accessRoutes.forEach(route => {
      router.addRoute(route);
    });

    // 重置访问的视图和缓存的视图
    dispatch('tagsView/delAllViews', null, { root: true });
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions
}; 