<template>
  <el-breadcrumb separator="/">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="item.path">
        <span v-if="index === breadcrumbs.length - 1 || item.redirect === 'noRedirect'" class="no-redirect">
          {{ item.meta.title }}
        </span>
        <a v-else @click.prevent="handleLink(item)">{{ item.meta.title }}</a>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { compile } from 'path-to-regexp';

const router = useRouter();
const route = useRoute();

// 面包屑数据
const breadcrumbs = ref([]);

// 获取面包屑数据
const getBreadcrumb = () => {
  const matched = route.matched.filter(item => item.meta && item.meta.title && item.meta.breadcrumb !== false);
  
  // 如果第一个元素的路径不是主页，则添加主页到面包屑开头
  if (matched.length > 0 && matched[0].path !== '/dashboard') {
    matched.unshift({
      path: '/dashboard',
      meta: { title: '主页' }
    });
  }
  
  breadcrumbs.value = matched;
};

// 初始化面包屑
getBreadcrumb();

// 路由变化时更新面包屑
watch(
  () => route.path,
  () => {
    getBreadcrumb();
  }
);

// 处理链接点击
const handleLink = (item) => {
  const { redirect, path } = item;
  
  if (redirect) {
    router.push(redirect);
    return;
  }
  
  // 将路径中的参数替换为实际值
  const pathCompiler = compile(path);
  const pathParams = pathCompiler(route.params);
  
  router.push(pathParams);
};
</script>

<style lang="scss" scoped>
.el-breadcrumb {
  display: inline-block;
  font-size: 14px;
  line-height: 60px;
  
  .no-redirect {
    color: #97a8be;
    cursor: text;
  }
  
  a {
    color: #666;
    font-weight: normal;
    
    &:hover {
      color: var(--el-color-primary);
    }
  }
}

/* 面包屑动画 */
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.5s;
}

.breadcrumb-enter-from,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(20px);
}

.breadcrumb-move {
  transition: all 0.5s;
}

.breadcrumb-leave-active {
  position: absolute;
}
</style> 