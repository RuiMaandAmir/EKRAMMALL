<template>
  <div class="sidebar-wrapper ekram-sidebar">
    <div class="sidebar-logo-container" v-if="!isCollapsed">
      <img src="../../assets/logo.png" alt="Logo" class="sidebar-logo" />
      <span class="sidebar-title">伊客拉穆商城</span>
    </div>
    
    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        :collapse-transition="false"
        mode="vertical"
        background-color="transparent"
        text-color="#303133"
      >
        <sidebar-item
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
          :is-collapsed="isCollapsed"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from 'vuex';
import SidebarItem from './SidebarItem.vue';

const route = useRoute();
const store = useStore();

// 侧边栏折叠状态
const isCollapsed = computed(() => store.state.app.sidebar.opened);

// 路由菜单
const routes = computed(() => {
  return store.state.permission.routes.filter(route => {
    return !route.hidden;
  });
});

// 当前激活的菜单
const activeMenu = computed(() => {
  const { meta, path } = route;
  if (meta.activeMenu) {
    return meta.activeMenu;
  }
  return path;
});
</script>

<style lang="scss" scoped>
.sidebar-wrapper {
  height: 100%;
  .sidebar-logo-container {
    height: 60px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    
    .sidebar-logo {
      width: 32px;
      height: 32px;
      margin-right: 12px;
    }
    
    .sidebar-title {
      font-size: 18px;
      font-weight: bold;
      color: var(--el-color-primary-dark-2);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}
</style> 