<template>
  <div class="app-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <el-form ref="formRef" :model="userInfo" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.name" disabled />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-tag v-for="role in userInfo.roles" :key="role" class="role-tag">
            {{ role }}
          </el-tag>
        </el-form-item>
        
        <el-form-item label="邮箱">
          <el-input v-model="userInfo.email" />
        </el-form-item>
        
        <el-form-item label="手机号码">
          <el-input v-model="userInfo.phone" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveUserProfile">保存</el-button>
          <el-button @click="goToChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';
import { updateProfile } from '@/api/user';

const router = useRouter();
const store = useStore();

const userInfo = reactive({
  name: '',
  email: '',
  phone: '',
  roles: []
});

onMounted(() => {
  const user = store.getters.user;
  userInfo.name = user.name || '';
  userInfo.email = user.email || '';
  userInfo.phone = user.phone || '';
  userInfo.roles = user.roles || [];
});

const saveUserProfile = async () => {
  try {
    await updateProfile({
      email: userInfo.email,
      phone: userInfo.phone
    });
    ElMessage.success('个人信息更新成功');
  } catch (error) {
    ElMessage.error('个人信息更新失败');
    console.error(error);
  }
};

const goToChangePassword = () => {
  router.push('/change-password');
};
</script>

<style lang="scss" scoped>
.profile-card {
  width: 600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-tag {
  margin-right: 8px;
}
</style> 