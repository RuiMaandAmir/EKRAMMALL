import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import './styles/index.scss'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建应用实例
const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(store)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn, // 使用中文语言包
  size: 'default' // 组件默认尺寸
})

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err, info)
}

// 挂载应用
app.mount('#app') 