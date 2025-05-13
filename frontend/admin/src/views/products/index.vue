<template>
  <div class="app-container">
    <div class="filter-container">
      <el-form :inline="true" :model="listQuery" class="demo-form-inline">
        <el-form-item label="产品名称">
          <el-input v-model="listQuery.name" placeholder="产品名称" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="listQuery.category" placeholder="选择分类" clearable>
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="listQuery.status" placeholder="选择状态" clearable>
            <el-option label="上架" value="true" />
            <el-option label="下架" value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="action-container">
      <el-button type="primary" @click="handleCreate">新增产品</el-button>
      <el-button type="danger" :disabled="selectedItems.length === 0" @click="handleBatchDelete">批量删除</el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column align="center" label="ID" width="80">
        <template #default="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="产品图片" width="100">
        <template #default="scope">
          <el-image 
            style="width: 60px; height: 60px" 
            :src="scope.row.cover" 
            :preview-src-list="[scope.row.cover]"
            fit="cover"
          >
            <template #error>
              <div class="image-error">
                <el-icon><picture-filled /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column label="产品名称" min-width="150">
        <template #default="scope">
          <span class="link-type" @click="handleDetail(scope.row)">{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120">
        <template #default="scope">
          <el-tag>{{ getCategoryName(scope.row.category) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="100" align="center">
        <template #default="scope">
          <span>¥{{ scope.row.price }}</span>
        </template>
      </el-table-column>
      <el-table-column label="库存" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.stock }}</span>
        </template>
      </el-table-column>
      <el-table-column label="销量" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.sales }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            active-color="#13ce66"
            inactive-color="#ff4949"
            @change="(val) => handleStatusChange(scope.row, val)"
          />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="150" align="center">
        <template #default="scope">
          <span>{{ formatDate(scope.row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
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

    <!-- 产品表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增产品' : '编辑产品'"
      width="700px"
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-width="100px"
        class="product-form"
      >
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品分类" prop="category">
          <el-select v-model="productForm.category" placeholder="请选择分类">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品价格" prop="price">
          <el-input-number v-model="productForm.price" :min="0" :precision="2" :step="0.1" />
        </el-form-item>
        <el-form-item label="产品库存" prop="stock">
          <el-input-number v-model="productForm.stock" :min="0" :precision="0" :step="1" />
        </el-form-item>
        <el-form-item label="产品封面" prop="cover">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/"
            :show-file-list="false"
            :on-success="handleImageSuccess"
            :before-upload="beforeImageUpload"
          >
            <img v-if="productForm.cover" :src="productForm.cover" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="图片集" prop="images">
          <el-upload
            class="product-images"
            action="/api/upload/"
            list-type="picture-card"
            :file-list="productForm.images"
            :on-success="handleImagesSuccess"
            :on-remove="handleRemoveImage"
          >
            <el-icon><plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="产品描述" prop="description">
          <el-input v-model="productForm.description" type="textarea" :rows="4" placeholder="请输入产品描述" />
        </el-form-item>
        <el-form-item label="详细内容" prop="content">
          <div style="border: 1px solid #ccc">
            <!-- 这里可以集成富文本编辑器 -->
            <el-input v-model="productForm.content" type="textarea" :rows="8" placeholder="请输入详细内容" />
          </div>
        </el-form-item>
        <el-form-item label="上架状态" prop="status">
          <el-switch v-model="productForm.status" active-text="上架" inactive-text="下架" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { PictureFilled, Plus } from '@element-plus/icons-vue';
import { 
  getProducts, 
  getCategories, 
  createProduct, 
  updateProduct, 
  deleteProduct, 
  updateProductStatus,
  batchDeleteProducts
} from '@/api/product';

// 列表数据
const list = ref([]);
const total = ref(0);
const listLoading = ref(false);
const selectedItems = ref([]);
const categories = ref([]);

// 查询条件
const listQuery = reactive({
  page: 1,
  limit: 20,
  name: '',
  category: '',
  status: ''
});

// 表单数据
const dialogVisible = ref(false);
const dialogType = ref('create');
const productFormRef = ref(null);
const productForm = reactive({
  id: undefined,
  name: '',
  category: '',
  price: 0,
  stock: 0,
  cover: '',
  images: [],
  description: '',
  content: '',
  status: true
});

// 表单验证规则
const productRules = {
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择产品分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入产品价格', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入产品库存', trigger: 'blur' }
  ],
  description: [
    { max: 255, message: '长度不能超过 255 个字符', trigger: 'blur' }
  ]
};

// 初始化
onMounted(() => {
  fetchCategories();
  fetchProducts();
});

// 获取产品分类
const fetchCategories = async () => {
  try {
    const res = await getCategories();
    categories.value = res.data;
  } catch (error) {
    console.error('获取分类失败:', error);
  }
};

// 根据分类ID获取分类名称
const getCategoryName = (categoryId) => {
  const category = categories.value.find(item => item.id === categoryId);
  return category ? category.name : '未分类';
};

// 获取产品列表
const fetchProducts = async () => {
  listLoading.value = true;
  try {
    const res = await getProducts(listQuery);
    list.value = res.data.items;
    total.value = res.data.total;
  } catch (error) {
    console.error('获取产品列表失败:', error);
  } finally {
    listLoading.value = false;
  }
};

// 表格多选
const handleSelectionChange = (val) => {
  selectedItems.value = val;
};

// 筛选
const handleFilter = () => {
  listQuery.page = 1;
  fetchProducts();
};

// 重置筛选
const resetFilter = () => {
  listQuery.name = '';
  listQuery.category = '';
  listQuery.status = '';
  handleFilter();
};

// 分页
const handleSizeChange = (val) => {
  listQuery.limit = val;
  fetchProducts();
};

const handleCurrentChange = (val) => {
  listQuery.page = val;
  fetchProducts();
};

// 新增产品
const handleCreate = () => {
  dialogType.value = 'create';
  resetForm();
  dialogVisible.value = true;
};

// 编辑产品
const handleEdit = (row) => {
  dialogType.value = 'edit';
  resetForm();
  // 转换图片数据结构以适应 el-upload
  const images = row.images ? row.images.map(img => ({
    url: img,
    name: img.substring(img.lastIndexOf('/') + 1)
  })) : [];
  
  Object.assign(productForm, { ...row, images });
  dialogVisible.value = true;
};

// 查看详情
const handleDetail = (row) => {
  // 可以跳转到详情页或弹出详情对话框
  ElMessage.info(`查看产品：${row.name}`);
};

// 删除产品
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确认删除产品 "${row.name}"?`, 
    '确认删除', 
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProduct(row.id);
      ElMessage.success('删除成功');
      fetchProducts();
    } catch (error) {
      console.error('删除产品失败:', error);
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

// 批量删除
const handleBatchDelete = () => {
  if (selectedItems.value.length === 0) return;
  
  ElMessageBox.confirm(
    `确认删除选中的 ${selectedItems.value.length} 件产品?`, 
    '确认批量删除', 
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const ids = selectedItems.value.map(item => item.id);
      await batchDeleteProducts(ids);
      ElMessage.success('批量删除成功');
      fetchProducts();
    } catch (error) {
      console.error('批量删除失败:', error);
      ElMessage.error('批量删除失败');
    }
  }).catch(() => {});
};

// 更新产品状态
const handleStatusChange = async (row, status) => {
  try {
    await updateProductStatus(row.id, status);
    ElMessage.success(`产品已${status ? '上架' : '下架'}`);
  } catch (error) {
    console.error('更新状态失败:', error);
    ElMessage.error('状态更新失败');
    // 恢复状态
    row.status = !status;
  }
};

// 重置表单
const resetForm = () => {
  productForm.id = undefined;
  productForm.name = '';
  productForm.category = '';
  productForm.price = 0;
  productForm.stock = 0;
  productForm.cover = '';
  productForm.images = [];
  productForm.description = '';
  productForm.content = '';
  productForm.status = true;
  
  if (productFormRef.value) {
    productFormRef.value.resetFields();
  }
};

// 提交表单
const submitForm = () => {
  productFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 处理图片数据，将 el-upload 的文件列表转换为 URL 数组
        const images = productForm.images.map(file => file.url || file.response.url);
        const data = { ...productForm, images };
        
        if (dialogType.value === 'create') {
          await createProduct(data);
          ElMessage.success('创建成功');
        } else {
          await updateProduct(data.id, data);
          ElMessage.success('更新成功');
        }
        
        dialogVisible.value = false;
        fetchProducts();
      } catch (error) {
        console.error('保存产品失败:', error);
        ElMessage.error('保存失败');
      }
    } else {
      return false;
    }
  });
};

// 封面上传
const handleImageSuccess = (response, file) => {
  productForm.cover = response.url;
};

// 图片集上传
const handleImagesSuccess = (response, file, fileList) => {
  productForm.images = fileList;
};

// 移除图片
const handleRemoveImage = (file, fileList) => {
  productForm.images = fileList;
};

// 上传前校验
const beforeImageUpload = (file) => {
  const isJPG = file.type === 'image/jpeg';
  const isPNG = file.type === 'image/png';
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isJPG && !isPNG) {
    ElMessage.error('上传图片只能是 JPG 或 PNG 格式!');
    return false;
  }
  if (!isLt2M) {
    ElMessage.error('上传图片大小不能超过 2MB!');
    return false;
  }
  return true;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.filter-container {
  padding-bottom: 20px;
  
  .el-form-item {
    margin-bottom: 15px;
  }
}

.action-container {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 30px;
  text-align: right;
}

.link-type {
  color: #409EFF;
  cursor: pointer;
  
  &:hover {
    text-decoration: underline;
  }
}

.avatar-uploader {
  .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    &:hover {
      border-color: #409EFF;
    }
  }
  
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 100px;
    height: 100px;
    line-height: 100px;
    text-align: center;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
    display: block;
  }
}

.product-form {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 20px;
}

.image-error {
  width: 60px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
}
</style> 