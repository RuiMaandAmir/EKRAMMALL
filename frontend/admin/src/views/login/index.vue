<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-logo">
        <img src="@/assets/logo.png" alt="Logo" class="logo-image">
        <h1 class="logo-title">伊客拉穆商城</h1>
        <p class="logo-subtitle">后台管理系统</p>
      </div>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form" autocomplete="on" label-position="left">
        <div class="form-title">管理员登录</div>
        
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            type="text"
            tabindex="1"
            autocomplete="on"
            clearable
          >
            <template #prefix>
              <el-icon class="el-input__icon"><user /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            :type="passwordVisible ? 'text' : 'password'"
            placeholder="密码"
            tabindex="2"
            autocomplete="on"
            clearable
            show-password
          >
            <template #prefix>
              <el-icon class="el-input__icon"><lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
        </el-form-item>

        <el-button :loading="loading" type="primary" class="login-button" @click.prevent="handleLogin">
          {{ loading ? '正在登录...' : '登 录' }}
        </el-button>
      </el-form>
    </div>

    <div class="login-footer">
      <p>© {{ new Date().getFullYear() }} 伊客拉穆商城 版权所有</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

const store = useStore();
const route = useRoute();
const router = useRouter();

// 登录表单
const loginForm = reactive({
  username: 'admin',
  password: 'admin123',
  rememberMe: false
});

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20个字符', trigger: 'blur' }
  ]
};

// 状态
const loading = ref(false);
const passwordVisible = ref(false);
const loginFormRef = ref(null);
const redirect = computed(() => route.query.redirect || '/');

// 处理登录
const handleLogin = () => {
  loginFormRef.value.validate(valid => {
    if (valid) {
      loading.value = true;
      store
        .dispatch('user/login', loginForm)
        .then(() => {
          ElMessage.success('登录成功');
          router.push({ path: redirect.value });
        })
        .catch(error => {
          console.error('登录失败:', error);
          ElMessage.error(error.message || '登录失败，请检查用户名和密码');
        })
        .finally(() => {
          loading.value = false;
        });
    } else {
      return false;
    }
  });
};

// 从本地存储恢复登录信息
onMounted(() => {
  // 如果之前保存了用户名，则恢复
  const savedUsername = localStorage.getItem('username');
  if (savedUsername) {
    loginForm.username = savedUsername;
    loginForm.rememberMe = true;
  }
});
</script>

<style lang="scss" scoped>
.login-container {
  height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;

  &:before {
    content: '';
    position: absolute;
    width: 200%;
    height: 200%;
    top: -50%;
    left: -50%;
    z-index: 0;
    background: url('@/assets/login-bg.svg') 0 0 no-repeat;
    background-size: 100% 100%;
    transform: rotate(30deg);
    opacity: 0.1;
  }
}

.login-box {
  width: 420px;
  padding: 30px;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.login-logo {
  text-align: center;
  margin-bottom: 30px;

  .logo-image {
    width: 80px;
    height: 80px;
    margin-bottom: 15px;
  }

  .logo-title {
    font-size: 28px;
    font-weight: bold;
    color: var(--el-color-primary);
    margin: 0 0 5px;
  }

  .logo-subtitle {
    font-size: 16px;
    color: #666;
    margin: 0;
  }
}

.form-title {
  font-size: 20px;
  color: #333;
  text-align: center;
  margin-bottom: 30px;
  font-weight: 500;
}

.login-form {
  .el-form-item {
    margin-bottom: 25px;
  }

  .el-input {
    height: 50px;
    
    :deep(.el-input__wrapper) {
      padding-left: 15px;
      box-shadow: 0 0 0 1px #dcdfe6 inset;
      
      &.is-focus {
        box-shadow: 0 0 0 1px var(--el-color-primary) inset;
      }
    }
    
    :deep(.el-input__icon) {
      font-size: 18px;
      color: #bbb;
    }
  }
}

.login-button {
  width: 100%;
  height: 50px;
  margin-top: 10px;
  font-size: 16px;
  border-radius: 4px;
}

.login-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .login-box {
    width: 90%;
    max-width: 400px;
  }
}
</style>