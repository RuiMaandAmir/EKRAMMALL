import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import store from '@/store';
import { getToken, clearAuth } from '@/utils/auth';
import router from '@/router';

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '/api', // url = base url + request url
  timeout: 15000 // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 如果存在token，则携带token
    if (store.getters.token) {
      config.headers['Authorization'] = `Bearer ${getToken()}`;
    }
    return config;
  },
  error => {
    console.log(error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data;

    // 如果响应不是200，则判断为错误
    if (response.status !== 200) {
      ElMessage({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      });

      // 401: 未授权；403: 禁止访问
      if (response.status === 401 || response.status === 403) {
        // 重新登录
        ElMessageBox.confirm('您已注销，可以取消停留在此页面，或再次登录', '确认注销', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('user/resetToken').then(() => {
            location.reload();
          });
        });
      }
      return Promise.reject(new Error(res.message || 'Error'));
    } else {
      return res;
    }
  },
  error => {
    console.log('Error:', error.response);
    
    if (error.response) {
      const { status, data } = error.response;
      
      // 401: 未授权 - token过期或无效
      if (status === 401) {
        // 清除登录信息
        clearAuth();
        
        if (router.currentRoute.value.path !== '/login') {
          ElMessageBox.confirm(
            '登录状态已过期，您可以继续留在该页面，或者重新登录',
            '系统提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            router.push(`/login?redirect=${router.currentRoute.value.fullPath}`);
          });
        }
      } 
      // 403: 禁止访问
      else if (status === 403) {
        router.push('/401');
      }
      // 500: 服务器错误
      else if (status === 500) {
        ElMessage({
          message: '服务器错误，请联系管理员',
          type: 'error',
          duration: 5 * 1000
        });
      } 
      // 其他错误
      else {
        ElMessage({
          message: data.message || `请求错误(${status})`,
          type: 'error',
          duration: 5 * 1000
        });
      }
    } else {
      ElMessage({
        message: '网络异常，请检查您的网络连接',
        type: 'error',
        duration: 5 * 1000
      });
    }
    
    return Promise.reject(error);
  }
);

export default service; 