<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button type="primary" @click="handleCreatePermission">添加权限</el-button>
    </div>

    <el-card>
      <div class="permission-tree-container">
        <el-tree
          ref="permissionTreeRef"
          :data="permissionList"
          :props="defaultProps"
          node-key="id"
          default-expand-all
        >
          <template #default="{ node, data }">
            <div class="custom-tree-node">
              <div class="node-label">
                <span>{{ node.label }}</span>
                <el-tag size="small" effect="plain" v-if="data.code">{{ data.code }}</el-tag>
              </div>
              <div class="node-actions">
                <el-button
                  size="small"
                  type="primary"
                  @click.stop="handleCreateChild(data)"
                >
                  添加子权限
                </el-button>
                <el-button
                  size="small"
                  type="success"
                  @click.stop="handleEdit(data)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click.stop="handleDelete(data)"
                  v-if="!data.is_system"
                >
                  删除
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </el-card>
    
    <!-- 权限编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form
        ref="permissionFormRef"
        :model="permissionForm"
        :rules="permissionRules"
        label-width="100px"
      >
        <el-form-item label="父级权限" v-if="dialogType !== 'edit'">
          <el-input v-model="parentPermissionName" disabled />
        </el-form-item>
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionForm.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限标识" prop="code">
          <el-input v-model="permissionForm.code" placeholder="请输入权限标识（可选）" />
        </el-form-item>
        <el-form-item label="路由地址" prop="path">
          <el-input v-model="permissionForm.path" placeholder="请输入路由地址（可选）" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="permissionForm.icon" placeholder="请输入图标名称（可选）">
            <template #suffix>
              <el-icon v-if="permissionForm.icon">
                <component :is="permissionForm.icon"></component>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="permissionForm.sort" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="permissionForm.type" placeholder="请选择权限类型">
            <el-option label="目录" value="directory" />
            <el-option label="菜单" value="menu" />
            <el-option label="按钮" value="button" />
            <el-option label="API" value="api" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="permissionForm.is_active" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="permissionForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入权限描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPermissionForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getPermissionList,
  createPermission,
  updatePermission,
  deletePermission
} from '@/api/permission';

// 权限列表
const permissionList = ref([]);
const permissionTreeRef = ref(null);

// 对话框控制
const dialogVisible = ref(false);
const dialogType = ref('create'); // 'create', 'createChild' 或 'edit'
const dialogTitle = computed(() => {
  if (dialogType.value === 'create') {
    return '添加权限';
  } else if (dialogType.value === 'createChild') {
    return '添加子权限';
  } else {
    return '编辑权限';
  }
});

// 当前操作的父权限
const parentPermission = ref(null);
const parentPermissionName = computed(() => {
  return parentPermission.value ? parentPermission.value.name : '根权限';
});

// 默认树形配置
const defaultProps = {
  children: 'children',
  label: 'name'
};

// 表单引用
const permissionFormRef = ref(null);

// 权限表单
const permissionForm = reactive({
  name: '',
  code: '',
  path: '',
  icon: '',
  parent_id: null,
  type: 'menu',
  sort: 0,
  is_active: true,
  description: ''
});

// 表单验证规则
const permissionRules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应为2到50个字符', trigger: 'blur' }
  ],
  code: [
    { pattern: /^[a-zA-Z0-9:_]+$/, message: '只能包含英文、数字、冒号和下划线', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择权限类型', trigger: 'change' }
  ]
};

// 获取权限列表
const fetchPermissions = async () => {
  try {
    const res = await getPermissionList();
    permissionList.value = res.data;
  } catch (error) {
    console.error('获取权限列表失败:', error);
    ElMessage.error('获取权限列表失败');
  }
};

// 初始化表单
const initForm = () => {
  permissionForm.name = '';
  permissionForm.code = '';
  permissionForm.path = '';
  permissionForm.icon = '';
  permissionForm.parent_id = null;
  permissionForm.type = 'menu';
  permissionForm.sort = 0;
  permissionForm.is_active = true;
  permissionForm.description = '';
};

// 添加顶级权限
const handleCreatePermission = () => {
  initForm();
  parentPermission.value = null;
  permissionForm.parent_id = null;
  dialogType.value = 'create';
  dialogVisible.value = true;
};

// 添加子权限
const handleCreateChild = (data) => {
  initForm();
  parentPermission.value = data;
  permissionForm.parent_id = data.id;
  dialogType.value = 'createChild';
  dialogVisible.value = true;
};

// 编辑权限
const handleEdit = (data) => {
  permissionForm.id = data.id;
  permissionForm.name = data.name;
  permissionForm.code = data.code || '';
  permissionForm.path = data.path || '';
  permissionForm.icon = data.icon || '';
  permissionForm.parent_id = data.parent_id;
  permissionForm.type = data.type;
  permissionForm.sort = data.sort || 0;
  permissionForm.is_active = data.is_active;
  permissionForm.description = data.description || '';
  dialogType.value = 'edit';
  dialogVisible.value = true;
};

// 提交权限表单
const submitPermissionForm = () => {
  permissionFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'edit') {
          await updatePermission(permissionForm.id, permissionForm);
          ElMessage.success('权限更新成功');
        } else {
          await createPermission(permissionForm);
          ElMessage.success('权限创建成功');
        }
        dialogVisible.value = false;
        fetchPermissions(); // 刷新权限列表
      } catch (error) {
        console.error('提交权限信息失败:', error);
        ElMessage.error('提交权限信息失败');
      }
    } else {
      return false;
    }
  });
};

// 删除权限
const handleDelete = (data) => {
  ElMessageBox.confirm(
    '确定要删除该权限吗？此操作将递归删除所有子权限，且不可恢复！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deletePermission(data.id);
      ElMessage.success('权限删除成功');
      fetchPermissions(); // 刷新权限列表
    } catch (error) {
      console.error('删除权限失败:', error);
      ElMessage.error('删除权限失败');
    }
  }).catch(() => {
    // 用户取消操作
  });
};

// 初始化
onMounted(() => {
  fetchPermissions();
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.filter-container {
  padding-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.permission-tree-container {
  margin-top: 10px;
  
  .custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
    
    .node-label {
      display: flex;
      align-items: center;
      
      .el-tag {
        margin-left: 10px;
      }
    }
    
    .node-actions {
      display: flex;
      gap: 5px;
    }
  }
}
</style> 