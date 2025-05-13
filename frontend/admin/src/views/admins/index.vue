<template>
  <div class="app-container">
    <div class="filter-container">
      <el-form :inline="true" :model="listQuery" class="demo-form-inline">
        <el-form-item label="管理员名称">
          <el-input v-model="listQuery.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="listQuery.is_active" placeholder="全部状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="handleCreateAdmin">添加管理员</el-button>
    </div>
    
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column align="center" label="ID" width="80">
        <template #default="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="头像" width="100">
        <template #default="scope">
          <el-avatar 
            :size="50" 
            :src="scope.row.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
          ></el-avatar>
        </template>
      </el-table-column>
      
      <el-table-column label="用户名" width="180">
        <template #default="scope">
          <span>{{ scope.row.username }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="真实姓名" width="120">
        <template #default="scope">
          <span>{{ scope.row.real_name || '-' }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="手机号" width="120" align="center">
        <template #default="scope">
          <span>{{ scope.row.phone || '-' }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="角色" width="120">
        <template #default="scope">
          <el-tag 
            v-for="role in scope.row.roles" 
            :key="role.id" 
            class="role-tag"
            type="success"
          >
            {{ role.name }}
          </el-tag>
          <span v-if="!scope.row.roles || scope.row.roles.length === 0">-</span>
        </template>
      </el-table-column>
      
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.is_active"
            :disabled="scope.row.id === 1" 
            @change="(val) => handleStatusChange(scope.row, val)"
          />
        </template>
      </el-table-column>
      
      <el-table-column label="最后登录" width="150" align="center">
        <template #default="scope">
          <span>{{ formatDate(scope.row.last_login_at) || '-' }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="创建时间" width="150" align="center">
        <template #default="scope">
          <span>{{ formatDate(scope.row.created_at) }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" min-width="200" align="center">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="handleEditAdmin(scope.row)"
            :disabled="scope.row.id === 1 && currentUserId !== 1"
          >
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="success" 
            @click="handleSetRole(scope.row)"
            :disabled="scope.row.id === 1 && currentUserId !== 1"
          >
            角色
          </el-button>
          <el-button 
            size="small" 
            type="warning" 
            @click="handleResetPassword(scope.row)"
            :disabled="scope.row.id === 1 && currentUserId !== 1"
          >
            重置密码
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDeleteAdmin(scope.row)"
            v-if="scope.row.id !== 1 && scope.row.id !== currentUserId"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="listQuery.page"
        v-model:page-size="listQuery.limit"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 管理员编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '添加管理员' : '编辑管理员'"
      width="500px"
    >
      <el-form
        ref="adminFormRef"
        :model="adminForm"
        :rules="adminRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="adminForm.username" 
            placeholder="请输入用户名" 
            :disabled="dialogType === 'edit'"
          ></el-input>
        </el-form-item>
        
        <el-form-item 
          label="密码" 
          prop="password"
          v-if="dialogType === 'create'"
        >
          <el-input 
            v-model="adminForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          ></el-input>
        </el-form-item>
        
        <el-form-item 
          label="确认密码" 
          prop="confirm_password"
          v-if="dialogType === 'create'"
        >
          <el-input 
            v-model="adminForm.confirm_password" 
            type="password" 
            placeholder="请再次输入密码"
            show-password
          ></el-input>
        </el-form-item>
        
        <el-form-item label="真实姓名" prop="real_name">
          <el-input 
            v-model="adminForm.real_name" 
            placeholder="请输入真实姓名"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input 
            v-model="adminForm.phone" 
            placeholder="请输入手机号"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="adminForm.email" 
            placeholder="请输入邮箱"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="adminForm.is_active"></el-switch>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAdminForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 角色设置对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      title="设置角色"
      width="500px"
    >
      <el-form>
        <el-form-item label="管理员">
          <span>{{ currentAdmin.username }}</span>
        </el-form-item>
        
        <el-form-item label="角色">
          <el-checkbox-group v-model="selectedRoles">
            <el-checkbox 
              v-for="role in roleList" 
              :key="role.id" 
              :label="role.id"
            >
              {{ role.name }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRoles">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useStore } from 'vuex';
import {
  getAdminList,
  createAdmin,
  updateAdmin,
  deleteAdmin,
  updateAdminStatus,
  resetPassword
} from '@/api/user';
import {
  getRoleList,
  getUserRoles,
  setUserRoles
} from '@/api/role';

const store = useStore();

// 当前登录用户ID
const currentUserId = computed(() => store.getters.userId);

// 列表数据
const list = ref([]);
const total = ref(0);
const listLoading = ref(false);

// 角色列表
const roleList = ref([]);

// 查询条件
const listQuery = reactive({
  page: 1,
  limit: 20,
  username: '',
  is_active: ''
});

// 对话框控制
const dialogVisible = ref(false);
const dialogType = ref('create'); // create 或 edit
const roleDialogVisible = ref(false);

// 表单引用
const adminFormRef = ref(null);

// 当前操作的管理员
const currentAdmin = ref({});
const selectedRoles = ref([]);

// 管理员表单
const adminForm = reactive({
  username: '',
  password: '',
  confirm_password: '',
  real_name: '',
  phone: '',
  email: '',
  is_active: true
});

// 表单验证规则
const validatePassword = (rule, value, callback) => {
  if (dialogType.value === 'edit') {
    callback();
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6个字符'));
  } else {
    callback();
  }
};

const validateConfirmPassword = (rule, value, callback) => {
  if (dialogType.value === 'edit') {
    callback();
  } else if (value !== adminForm.password) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const adminRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度应为3到20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};

// 获取管理员列表
const fetchAdmins = async () => {
  listLoading.value = true;
  try {
    const res = await getAdminList(listQuery);
    list.value = res.data.items;
    total.value = res.data.total;
  } catch (error) {
    console.error('获取管理员列表失败:', error);
    ElMessage.error('获取管理员列表失败');
  } finally {
    listLoading.value = false;
  }
};

// 获取角色列表
const fetchRoles = async () => {
  try {
    const res = await getRoleList();
    roleList.value = res.data;
  } catch (error) {
    console.error('获取角色列表失败:', error);
    ElMessage.error('获取角色列表失败');
  }
};

// 筛选
const handleFilter = () => {
  listQuery.page = 1;
  fetchAdmins();
};

// 重置筛选
const resetFilter = () => {
  listQuery.username = '';
  listQuery.is_active = '';
  handleFilter();
};

// 分页
const handleSizeChange = (val) => {
  listQuery.limit = val;
  fetchAdmins();
};

const handleCurrentChange = (val) => {
  listQuery.page = val;
  fetchAdmins();
};

// 初始化表单
const initForm = () => {
  adminForm.username = '';
  adminForm.password = '';
  adminForm.confirm_password = '';
  adminForm.real_name = '';
  adminForm.phone = '';
  adminForm.email = '';
  adminForm.is_active = true;
};

// 添加管理员
const handleCreateAdmin = () => {
  initForm();
  dialogType.value = 'create';
  dialogVisible.value = true;
};

// 编辑管理员
const handleEditAdmin = (row) => {
  dialogType.value = 'edit';
  adminForm.id = row.id;
  adminForm.username = row.username;
  adminForm.real_name = row.real_name || '';
  adminForm.phone = row.phone || '';
  adminForm.email = row.email || '';
  adminForm.is_active = row.is_active;
  dialogVisible.value = true;
};

// 提交管理员表单
const submitAdminForm = () => {
  adminFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'create') {
          await createAdmin(adminForm);
          ElMessage.success('管理员创建成功');
        } else {
          const updateData = {
            real_name: adminForm.real_name,
            phone: adminForm.phone,
            email: adminForm.email,
            is_active: adminForm.is_active
          };
          await updateAdmin(adminForm.id, updateData);
          ElMessage.success('管理员更新成功');
        }
        dialogVisible.value = false;
        fetchAdmins(); // 刷新列表
      } catch (error) {
        console.error('提交管理员信息失败:', error);
        ElMessage.error('提交管理员信息失败: ' + (error.response?.data?.message || error.message || '未知错误'));
      }
    } else {
      return false;
    }
  });
};

// 删除管理员
const handleDeleteAdmin = (row) => {
  ElMessageBox.confirm(
    '确定要删除该管理员吗？此操作将不可逆。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteAdmin(row.id);
      ElMessage.success('管理员删除成功');
      fetchAdmins(); // 刷新列表
    } catch (error) {
      console.error('删除管理员失败:', error);
      ElMessage.error('删除管理员失败: ' + (error.response?.data?.message || error.message || '未知错误'));
    }
  }).catch(() => {
    // 用户取消操作
  });
};

// 更新管理员状态
const handleStatusChange = async (row, status) => {
  try {
    await updateAdminStatus(row.id, status);
    ElMessage.success(`已${status ? '启用' : '禁用'}该管理员`);
  } catch (error) {
    console.error('更新管理员状态失败:', error);
    ElMessage.error('更新管理员状态失败: ' + (error.response?.data?.message || error.message || '未知错误'));
    // 恢复状态
    row.is_active = !status;
  }
};

// 重置密码
const handleResetPassword = (row) => {
  ElMessageBox.confirm(
    '确定要重置该管理员的密码吗？重置后将生成随机密码。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await resetPassword(row.id);
      ElMessageBox.alert(
        `新密码: ${res.data.password}`,
        '密码重置成功',
        {
          confirmButtonText: '确定',
          callback: () => {}
        }
      );
    } catch (error) {
      console.error('重置密码失败:', error);
      ElMessage.error('重置密码失败: ' + (error.response?.data?.message || error.message || '未知错误'));
    }
  }).catch(() => {
    // 用户取消操作
  });
};

// 设置角色
const handleSetRole = async (row) => {
  currentAdmin.value = row;
  
  try {
    // 获取该管理员已有的角色
    const res = await getUserRoles(row.id);
    selectedRoles.value = res.data.map(r => r.id);
    
    // 显示对话框
    roleDialogVisible.value = true;
  } catch (error) {
    console.error('获取管理员角色失败:', error);
    ElMessage.error('获取管理员角色失败: ' + (error.response?.data?.message || error.message || '未知错误'));
  }
};

// 提交角色设置
const submitRoles = async () => {
  try {
    await setUserRoles(currentAdmin.value.id, selectedRoles.value);
    ElMessage.success('角色设置成功');
    roleDialogVisible.value = false;
    fetchAdmins(); // 刷新列表
  } catch (error) {
    console.error('设置角色失败:', error);
    ElMessage.error('设置角色失败: ' + (error.response?.data?.message || error.message || '未知错误'));
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 初始化
onMounted(() => {
  fetchAdmins();
  fetchRoles();
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.filter-container {
  padding-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 30px;
  text-align: right;
}

.role-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style> 