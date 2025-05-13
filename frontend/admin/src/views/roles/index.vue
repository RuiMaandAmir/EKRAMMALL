<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button type="primary" @click="handleCreateRole">添加角色</el-button>
    </div>
    
    <el-table
      v-loading="listLoading"
      :data="roleList"
      border
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="name" label="角色名称" width="180" />
      <el-table-column prop="description" label="角色描述" min-width="220" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.is_active"
            @change="(val) => handleStatusChange(scope.row, val)"
          />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180" align="center">
        <template #default="scope">
          <span>{{ formatDate(scope.row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="handleEditRole(scope.row)"
          >
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="success" 
            @click="handleSetPermission(scope.row)"
          >
            权限
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDeleteRole(scope.row)"
            v-if="scope.row.id !== 1"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 角色编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '添加角色' : '编辑角色'"
      width="500px"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleRules"
        label-width="100px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色标识" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入角色标识（英文）" />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="roleForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRoleForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 权限设置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="权限设置"
      width="600px"
    >
      <el-form>
        <el-form-item label="角色名称">
          <span>{{ currentRole.name }}</span>
        </el-form-item>
        
        <el-form-item label="权限">
          <el-tree
            ref="permissionTreeRef"
            :data="permissionTree"
            :props="{ label: 'name', children: 'children' }"
            show-checkbox
            node-key="id"
            default-expand-all
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="permissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPermissions">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getRoleList,
  createRole,
  updateRole,
  deleteRole,
  updateRoleStatus,
  getRolePermissions,
  updateRolePermissions,
  getPermissionTree
} from '@/api/role';

// 角色列表数据
const roleList = ref([]);
const listLoading = ref(false);

// 对话框控制
const dialogVisible = ref(false);
const dialogType = ref('create'); // 'create' 或 'edit'
const permissionDialogVisible = ref(false);

// 表单引用
const roleFormRef = ref(null);
const permissionTreeRef = ref(null);

// 当前操作的角色
const currentRole = ref({});

// 权限树数据
const permissionTree = ref([]);

// 角色表单
const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
});

// 表单验证规则
const roleRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度应为2到20个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含英文、数字和下划线', trigger: 'blur' }
  ]
};

// 获取角色列表
const fetchRoles = async () => {
  listLoading.value = true;
  try {
    const res = await getRoleList();
    roleList.value = res.data;
  } catch (error) {
    console.error('获取角色列表失败:', error);
    ElMessage.error('获取角色列表失败');
  } finally {
    listLoading.value = false;
  }
};

// 初始化表单
const initForm = () => {
  roleForm.name = '';
  roleForm.code = '';
  roleForm.description = '';
  roleForm.is_active = true;
};

// 添加角色
const handleCreateRole = () => {
  initForm();
  dialogType.value = 'create';
  dialogVisible.value = true;
};

// 编辑角色
const handleEditRole = (row) => {
  dialogType.value = 'edit';
  roleForm.id = row.id;
  roleForm.name = row.name;
  roleForm.code = row.code;
  roleForm.description = row.description;
  roleForm.is_active = row.is_active;
  dialogVisible.value = true;
};

// 提交角色表单
const submitRoleForm = () => {
  roleFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'create') {
          await createRole(roleForm);
          ElMessage.success('角色创建成功');
        } else {
          await updateRole(roleForm.id, roleForm);
          ElMessage.success('角色更新成功');
        }
        dialogVisible.value = false;
        fetchRoles(); // 刷新角色列表
      } catch (error) {
        console.error('提交角色信息失败:', error);
        ElMessage.error('提交角色信息失败');
      }
    } else {
      return false;
    }
  });
};

// 删除角色
const handleDeleteRole = (row) => {
  ElMessageBox.confirm(
    '确定要删除该角色吗？此操作将不可逆，并移除所有使用该角色的用户权限。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteRole(row.id);
      ElMessage.success('角色删除成功');
      fetchRoles(); // 刷新角色列表
    } catch (error) {
      console.error('删除角色失败:', error);
      ElMessage.error('删除角色失败');
    }
  }).catch(() => {
    // 用户取消操作
  });
};

// 更新角色状态
const handleStatusChange = async (row, status) => {
  try {
    await updateRoleStatus(row.id, status);
    ElMessage.success(`已${status ? '启用' : '禁用'}该角色`);
  } catch (error) {
    console.error('更新角色状态失败:', error);
    ElMessage.error('更新角色状态失败');
    // 恢复状态
    row.is_active = !status;
  }
};

// 打开权限设置对话框
const handleSetPermission = async (row) => {
  currentRole.value = row;
  
  try {
    // 获取权限树
    const treeRes = await getPermissionTree();
    permissionTree.value = treeRes.data;
    
    // 获取该角色已有的权限
    const permRes = await getRolePermissions(row.id);
    const checkedKeys = permRes.data.map(p => p.id);
    
    // 显示对话框
    permissionDialogVisible.value = true;
    
    // 等待DOM更新后设置选中节点
    setTimeout(() => {
      permissionTreeRef.value.setCheckedKeys(checkedKeys);
    }, 100);
  } catch (error) {
    console.error('获取权限数据失败:', error);
    ElMessage.error('获取权限数据失败');
  }
};

// 提交权限设置
const submitPermissions = async () => {
  try {
    const checkedKeys = permissionTreeRef.value.getCheckedKeys();
    const halfCheckedKeys = permissionTreeRef.value.getHalfCheckedKeys();
    const allCheckedKeys = [...checkedKeys, ...halfCheckedKeys];
    
    await updateRolePermissions(currentRole.value.id, allCheckedKeys);
    ElMessage.success('权限设置成功');
    permissionDialogVisible.value = false;
  } catch (error) {
    console.error('提交权限设置失败:', error);
    ElMessage.error('提交权限设置失败');
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
</style> 