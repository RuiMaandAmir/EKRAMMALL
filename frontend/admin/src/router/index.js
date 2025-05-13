import { createRouter, createWebHistory } from 'vue-router';
import Layout from '@/layout/index.vue';
// 启用促销路由模块
import promotionRoutes from './modules/promotion';
// 启用商品路由模块
import productRoutes from './modules/product';

/**
 * 路由配置
 * 
 * meta: {
 *  title: '标题',          // 页面标题，必填
 *  icon: 'svg图标名称',    // 图标，选填
 *  affix: true,           // 固定在标签页上，选填
 *  activeMenu: '/xxx',    // 高亮显示的菜单项，选填
 *  breadcrumb: false,     // 是否在面包屑中显示，默认true
 *  roles: ['admin','editor'] // 允许的角色，选填
 * }
 */

export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404.vue'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401.vue'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        name: 'Dashboard',
        meta: { title: '仪表盘', icon: 'Odometer', affix: true }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心' }
      }
    ]
  },
  {
    path: '/change-password',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '',
        name: 'ChangePassword',
        component: () => import('@/views/profile/change-password.vue'),
        meta: { title: '修改密码' }
      }
    ]
  }
];

/**
 * 动态路由
 * 需要根据用户角色动态加载的路由
 */
export const asyncRoutes = [
  /* 已启用的功能模块 */
  
  // 促销路由模块
  promotionRoutes,
  
  // 商品路由模块
  productRoutes,
  
  // 404页必须放在最后
  { path: '/:catchAll(.*)', redirect: '/404', hidden: true }
];

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: constantRoutes
});

export function resetRouter() {
  const newRouter = createRouter({
    history: createWebHistory(),
    scrollBehavior: () => ({ top: 0 }),
    routes: constantRoutes
  });
  
  // 重置路由
  router.matcher = newRouter.matcher;
}

export default router; 