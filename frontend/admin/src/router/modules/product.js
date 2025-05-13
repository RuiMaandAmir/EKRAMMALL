import Layout from '@/layout/index.vue'

const productRouter = {
  path: '/product',
  component: Layout,
  redirect: '/product/list',
  name: 'Product',
  meta: {
    title: '商品管理',
    icon: 'Shopping'
  },
  children: [
    {
      path: 'list',
      component: () => import('@/views/products/List.vue'),
      name: 'ProductList',
      meta: { title: '商品列表' }
    },
    {
      path: 'create',
      component: () => import('@/views/products/Detail.vue'),
      name: 'ProductCreate',
      meta: { title: '创建商品', activeMenu: '/product/list' },
      hidden: true
    },
    {
      path: 'edit/:id',
      component: () => import('@/views/products/Detail.vue'),
      name: 'ProductEdit',
      meta: { title: '编辑商品', activeMenu: '/product/list' },
      hidden: true
    },
    {
      path: 'category',
      component: () => import('@/views/products/Category.vue'),
      name: 'ProductCategory',
      meta: { title: '商品分类' }
    }
  ]
}

export default productRouter 