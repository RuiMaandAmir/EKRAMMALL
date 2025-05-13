<template>
  <div class="app-container" :class="{ 'is-collapsed': isCollapsed }">
    <!-- 顶部导航栏 -->
    <div class="navbar-container ekram-header">
      <div class="left-section">
        <!-- 折叠按钮 -->
        <div class="hamburger-container" @click="toggleSidebar">
          <el-icon class="hamburger" :class="{ 'is-active': !isCollapsed }">
            <Fold v-if="isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>

        <!-- Logo -->
        <div class="logo-container">
          <img src="../assets/logo.png" alt="Logo" class="logo-image" />
          <span class="logo-text ekram-logo">伊客拉穆商城</span>
        </div>
      </div>
      
      <div class="right-section">
        <!-- 面包屑导航 -->
        <breadcrumb class="breadcrumb-container" />
        
        <!-- 用户菜单 -->
        <div class="user-container">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-wrapper">
              <img :src="avatar" class="user-avatar" />
              <span class="user-name">{{ username }}</span>
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="changePassword">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 侧边栏 -->
    <div class="layout-container">
      <sidebar class="sidebar-container" :class="{ 'is-collapsed': isCollapsed }" />
      
      <!-- 主内容区 -->
      <div class="main-container" :class="{ 'is-collapsed': isCollapsed }">
        <div class="content-container">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <keep-alive :include="cachedViews">
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { ElMessage, ElMessageBox } from 'element-plus';
import Sidebar from './components/Sidebar.vue';
import Breadcrumb from './components/Breadcrumb.vue';

const store = useStore();
const router = useRouter();

// 侧边栏折叠状态
const isCollapsed = computed(() => store.state.app.sidebar.opened);

// 用户信息
const username = computed(() => store.state.user.name || '管理员');
const avatar = computed(() => store.state.user.avatar || '/assets/default-avatar.png');

// 缓存的视图
const cachedViews = computed(() => store.state.tagsView.cachedViews);

// 切换侧边栏
const toggleSidebar = () => {
  store.dispatch('app/toggleSidebar');
};

// 下拉菜单命令处理
const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      store.dispatch('user/logout').then(() => {
        router.push('/login');
        ElMessage.success('已安全退出登录');
      });
    }).catch(() => {});
  } else if (command === 'profile') {
    router.push('/profile');
  } else if (command === 'changePassword') {
    router.push('/change-password');
  }
};

// 初始化获取用户信息
onMounted(() => {
  if (store.state.user.token) {
    // 获取用户信息
    store.dispatch('user/getInfo');
  }
});
</script>

<style lang="scss" scoped>
.app-container {
  position: relative;
  height: 100%;
  width: 100%;
}

.navbar-container {
  height: 60px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
  z-index: 1002;

  .left-section {
    display: flex;
    align-items: center;
    
    .logo-container {
      display: flex;
      align-items: center;
      margin-left: 10px;
      
      .logo-image {
        width: 32px;
        height: 32px;
        margin-right: 8px;
      }
      
      .logo-text {
        font-size: 18px;
      }
    }
  }
  
  .right-section {
    display: flex;
    align-items: center;
    
    .breadcrumb-container {
      margin-right: 20px;
    }
    
    .user-container {
      .user-wrapper {
        display: flex;
        align-items: center;
        cursor: pointer;
        padding: 0 10px;
        height: 40px;
        
        &:hover {
          background-color: rgba(0, 0, 0, 0.025);
          border-radius: 20px;
        }
        
        .user-avatar {
          width: 30px;
          height: 30px;
          border-radius: 15px;
          margin-right: 8px;
        }
        
        .user-name {
          font-size: 14px;
          margin-right: 4px;
        }
      }
    }
  }
}

.layout-container {
  padding-top: 60px;
  display: flex;
  min-height: calc(100vh - 60px);
}

.content-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
  overflow-y: auto;
}
</style> 