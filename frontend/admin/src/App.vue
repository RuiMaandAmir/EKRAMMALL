<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

onMounted(() => {
  // 检查用户是否已登录，如果未登录则跳转到登录页
  const token = localStorage.getItem('admin_token');
  if (!token && router.currentRoute.value.path !== '/login') {
    router.push('/login');
  }
});
</script>

<style lang="scss">
#app {
  width: 100%;
  height: 100%;
}
</style> 