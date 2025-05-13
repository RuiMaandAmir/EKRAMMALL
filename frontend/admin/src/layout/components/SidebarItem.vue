<template>
  <div v-if="!item.hidden">
    <!-- 无子菜单的情况 -->
    <template v-if="hasOneShowingChild(item.children, item) && (!onlyOneChild.children || onlyOneChild.noShowingChildren) && !item.alwaysShow">
      <app-link :to="resolvePath(onlyOneChild.path)">
        <el-menu-item :index="resolvePath(onlyOneChild.path)" :class="{'submenu-title-noDropdown': !isNest}">
          <el-icon v-if="onlyOneChild.meta && onlyOneChild.meta.icon">
            <component :is="onlyOneChild.meta.icon"></component>
          </el-icon>
          <template #title>
            <span v-if="onlyOneChild.meta && onlyOneChild.meta.title">{{ onlyOneChild.meta.title }}</span>
          </template>
        </el-menu-item>
      </app-link>
    </template>

    <!-- 有子菜单的情况 -->
    <el-sub-menu v-else :index="resolvePath(item.path)">
      <template #title>
        <el-icon v-if="item.meta && item.meta.icon">
          <component :is="item.meta.icon"></component>
        </el-icon>
        <span v-if="item.meta && item.meta.title">{{ item.meta.title }}</span>
      </template>
      
      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :is-nest="true"
        :item="child"
        :base-path="resolvePath(child.path)"
        :is-collapsed="isCollapsed"
      />
    </el-sub-menu>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue';
import { isExternal } from '@/utils/validate';
import AppLink from './Link.vue';
import path from 'path-browserify';

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  isNest: {
    type: Boolean,
    default: false
  },
  basePath: {
    type: String,
    default: ''
  },
  isCollapsed: {
    type: Boolean,
    default: false
  }
});

const onlyOneChild = ref(null);

// 判断是否只有一个可显示的子菜单
const hasOneShowingChild = (children = [], parent) => {
  const showingChildren = children.filter(item => {
    if (item.hidden) {
      return false;
    } else {
      // 将唯一的子路由赋值给onlyOneChild
      onlyOneChild.value = item;
      return true;
    }
  });

  // 如果只有一个子路由，就显示这个子路由
  if (showingChildren.length === 1) {
    return true;
  }

  // 如果没有子路由，就显示父路由
  if (showingChildren.length === 0) {
    onlyOneChild.value = { ...parent, path: '', noShowingChildren: true };
    return true;
  }

  return false;
};

// 解析路径
const resolvePath = (routePath) => {
  if (isExternal(routePath)) {
    return routePath;
  }
  if (isExternal(props.basePath)) {
    return props.basePath;
  }
  return path.resolve(props.basePath, routePath);
};
</script> 