import Layout from '@/layout/index.vue'

const promotionRouter = {
  path: '/promotion',
  component: Layout,
  redirect: '/promotion/list',
  name: 'Promotion',
  meta: {
    title: '促销管理',
    icon: 'Shopping'
  },
  children: [
    {
      path: 'list',
      component: () => import('@/views/promotion/List.vue'),
      name: 'PromotionList',
      meta: { title: '促销活动列表' }
    },
    {
      path: 'detail/:id',
      component: () => import('@/views/promotion/Detail.vue'),
      name: 'PromotionDetail',
      meta: { title: '活动详情', activeMenu: '/promotion/list' },
      hidden: true
    },
    {
      path: 'create',
      component: () => import('@/views/promotion/Detail.vue'),
      name: 'PromotionCreate',
      meta: { title: '创建活动', activeMenu: '/promotion/list' },
      hidden: true
    },
    {
      path: 'export',
      component: () => import('@/views/promotion/Export.vue'),
      name: 'PromotionExport',
      meta: { title: '数据导出' }
    },
    {
      path: 'products/:activityId',
      name: 'PromotionProducts',
      component: () => import('@/views/promotion/Products.vue'),
      meta: {
        title: '促销商品管理',
        activeMenu: '/promotion/list'
      },
      hidden: true
    }
  ]
}

export default promotionRouter 