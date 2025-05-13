import { createStore } from 'vuex';
import getters from './getters';
import app from './modules/app';
import settings from './modules/settings';
import user from './modules/user';
import permission from './modules/permission';
import tagsView from './modules/tagsView';

const store = createStore({
  modules: {
    app,
    settings,
    user,
    permission,
    tagsView
  },
  getters
});

export default store; 