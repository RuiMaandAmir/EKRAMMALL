import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 引入样式文件
import './assets/styles/main.css'

// 创建Vue应用实例
const app = createApp(App)

// 使用插件
app.use(router)
app.use(store)

// 挂载应用
app.mount('#app') 