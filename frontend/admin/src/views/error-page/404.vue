<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <div class="error-message">找不到页面</div>
      <div class="error-desc">抱歉，您访问的页面不存在</div>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  router.push('/');
};
</script>

<style lang="scss" scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.error-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  color: #4caf50;
  margin: 0;
}

.error-message {
  font-size: 24px;
  color: #303133;
  margin: 20px 0;
}

.error-desc {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
}
</style> 