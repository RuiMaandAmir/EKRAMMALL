<template>
  <div class="category-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品分类管理</span>
          <el-button type="primary" @click="handleAddCategory">新增分类</el-button>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="categoryList"
        border
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children' }"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="description" label="分类描述" min-width="250" />
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="230" align="center">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="handleEdit(scope.row)"
            >编辑</el-button>
            <el-button 
              size="small" 
              type="success" 
              v-if="!scope.row.parent_id"
              @click="handleAddSubCategory(scope.row)"
            >添加子分类</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDelete(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 分类表单对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item v-if="categoryForm.parent_id" label="父级分类">
          <el-input v-model="parentCategoryName" disabled />
        </el-form-item>
        
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        
        <el-form-item label="分类描述" prop="description">
          <el-input 
            v-model="categoryForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入分类描述"
          />
        </el-form-item>
        
        <el-form-item label="分类图标" prop="icon">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/image/"
            :headers="{ Authorization: `Bearer ${getToken()}` }"
            :show-file-list="false"
            :on-success="handleIconSuccess"
            :before-upload="beforeIconUpload"
          >
            <img v-if="categoryForm.icon" :src="categoryForm.icon" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="排序权重" prop="sort_order">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
        
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="categoryForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCategory">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/product';
import { getToken } from '@/utils/auth';

const loading = ref(false);
const categoryList = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('新增分类');
const categoryFormRef = ref(null);
const parentCategoryName = ref('');

// 分类表单数据
const categoryForm = reactive({
  id: undefined,
  parent_id: undefined,
  name: '',
  description: '',
  icon: '',
  sort_order: 0,
  is_active: true
});

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '最多200个字符', trigger: 'blur' }
  ]
};

// 获取分类列表
const fetchCategories = async () => {
  loading.value = true;
  try {
    const response = await getCategories();
    // 转换成树形结构
    categoryList.value = buildCategoryTree(response.data || []);
  } catch (error) {
    console.error('获取分类列表失败:', error);
    ElMessage.error('获取分类列表失败');
  } finally {
    loading.value = false;
  }
};

// 构建分类树形结构
const buildCategoryTree = (categories) => {
  const categoryMap = {};
  const result = [];

  // 先构建一个以id为键的映射
  categories.forEach(category => {
    categoryMap[category.id] = { ...category, children: [] };
  });

  // 构建树形结构
  categories.forEach(category => {
    if (category.parent_id) {
      // 有父级，添加到父级的children中
      if (categoryMap[category.parent_id]) {
        categoryMap[category.parent_id].children.push(categoryMap[category.id]);
      }
    } else {
      // 没有父级，直接添加到结果数组
      result.push(categoryMap[category.id]);
    }
  });

  return result;
};

// 新增分类
const handleAddCategory = () => {
  resetCategoryForm();
  dialogTitle.value = '新增分类';
  dialogVisible.value = true;
};

// 新增子分类
const handleAddSubCategory = (row) => {
  resetCategoryForm();
  categoryForm.parent_id = row.id;
  parentCategoryName.value = row.name;
  dialogTitle.value = '新增子分类';
  dialogVisible.value = true;
};

// 编辑分类
const handleEdit = (row) => {
  resetCategoryForm();
  Object.keys(categoryForm).forEach(key => {
    if (row[key] !== undefined) {
      categoryForm[key] = row[key];
    }
  });

  if (row.parent_id) {
    // 查找父级分类名称
    const findParent = (categories, parentId) => {
      for (const category of categories) {
        if (category.id === parentId) {
          return category.name;
        }
        if (category.children && category.children.length > 0) {
          const name = findParent(category.children, parentId);
          if (name) return name;
        }
      }
      return '';
    };
    parentCategoryName.value = findParent(categoryList.value, row.parent_id);
  }

  dialogTitle.value = '编辑分类';
  dialogVisible.value = true;
};

// 删除分类
const handleDelete = (row) => {
  if (row.children && row.children.length > 0) {
    ElMessage.warning('该分类下有子分类，不能删除');
    return;
  }

  ElMessageBox.confirm('确定要删除该分类吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteCategory(row.id);
      ElMessage.success('删除成功');
      fetchCategories();
    } catch (error) {
      console.error('删除分类失败:', error);
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

// 重置分类表单
const resetCategoryForm = () => {
  Object.keys(categoryForm).forEach(key => {
    if (key === 'is_active') {
      categoryForm[key] = true;
    } else if (key === 'sort_order') {
      categoryForm[key] = 0;
    } else {
      categoryForm[key] = undefined;
    }
  });
  parentCategoryName.value = '';
  if (categoryFormRef.value) {
    categoryFormRef.value.resetFields();
  }
};

// 图标上传前的验证
const beforeIconUpload = (file) => {
  const isJPG = file.type === 'image/jpeg';
  const isPNG = file.type === 'image/png';
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isJPG && !isPNG) {
    ElMessage.error('上传图标只能是 JPG 或 PNG 格式!');
    return false;
  }
  if (!isLt2M) {
    ElMessage.error('上传图标大小不能超过 2MB!');
    return false;
  }
  return true;
};

// 图标上传成功处理
const handleIconSuccess = (response, file) => {
  if (response.code === 200) {
    categoryForm.icon = response.data.url;
  } else {
    ElMessage.error('上传失败');
  }
};

// 提交分类
const submitCategory = () => {
  categoryFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (categoryForm.id) {
          // 编辑模式
          await updateCategory(categoryForm.id, categoryForm);
          ElMessage.success('更新成功');
        } else {
          // 新增模式
          await createCategory(categoryForm);
          ElMessage.success('创建成功');
        }
        dialogVisible.value = false;
        fetchCategories();
      } catch (error) {
        console.error('保存分类失败:', error);
        ElMessage.error('保存失败');
      }
    }
  });
};

onMounted(() => {
  fetchCategories();
});
</script>

<style lang="scss" scoped>
.category-management {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .avatar-uploader {
    width: 100px;
    height: 100px;
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    &:hover {
      border-color: #409EFF;
    }
    
    .avatar {
      width: 100px;
      height: 100px;
      display: block;
    }
    
    .avatar-uploader-icon {
      font-size: 28px;
      color: #8c939d;
      width: 100px;
      height: 100px;
      line-height: 100px;
      text-align: center;
    }
  }
}
</style> 