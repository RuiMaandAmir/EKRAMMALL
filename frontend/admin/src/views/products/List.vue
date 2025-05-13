<template>
  <div class="product-list">
    <div class="filter-container">
      <el-form :inline="true" :model="queryParams" class="form-inline">
        <el-form-item label="商品名称">
          <el-input v-model="queryParams.name" placeholder="输入商品名称" clearable class="filter-item" />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="queryParams.category" placeholder="选择分类" clearable class="filter-item">
            <el-option label="全部" value="" />
            <el-option 
              v-for="item in categoryOptions" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="选择状态" clearable class="filter-item">
            <el-option label="全部" value="" />
            <el-option label="上架" value="active" />
            <el-option label="下架" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="action-container">
      <el-button type="primary" @click="handleCreate">新增商品</el-button>
      <el-button type="danger" @click="handleBatchDelete" :disabled="selectedProducts.length === 0">
        批量删除
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%; margin-top: 20px;"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column label="商品图片" width="100" align="center">
        <template #default="scope">
          <el-image 
            :src="scope.row.image_url || '/placeholder-image.png'"
            style="width: 50px; height: 50px"
            fit="cover"
            :preview-src-list="[scope.row.image_url]"
          />
        </template>
      </el-table-column>
      <el-table-column prop="name" label="商品名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="category_name" label="商品分类" width="120" />
      <el-table-column prop="price" label="价格" width="100" align="right">
        <template #default="scope">
          ¥{{ scope.row.price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="80" align="center" />
      <el-table-column prop="sales" label="销量" width="80" align="center" />
      <el-table-column prop="status" label="状态" width="80" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
            {{ scope.row.status === 'active' ? '上架' : '下架' }}
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
            :type="scope.row.status === 'active' ? 'warning' : 'success'" 
            @click="handleToggleStatus(scope.row)"
          >{{ scope.row.status === 'active' ? '下架' : '上架' }}</el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="limit"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  getProducts, 
  deleteProduct, 
  updateProductStatus,
  batchDeleteProducts
} from '@/api/product';
import { getCategories } from '@/api/product';

const router = useRouter();
const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const page = ref(1);
const limit = ref(10);
const selectedProducts = ref([]);
const categoryOptions = ref([]);

const queryParams = reactive({
  name: '',
  category: '',
  status: '',
  page: 1,
  limit: 10
});

// 获取商品列表数据
const fetchData = async () => {
  loading.value = true;
  try {
    queryParams.page = page.value;
    queryParams.limit = limit.value;
    
    const response = await getProducts(queryParams);
    tableData.value = response.data.items || [];
    total.value = response.data.total || 0;
  } catch (error) {
    console.error('获取商品列表失败:', error);
    ElMessage.error('获取商品列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取商品分类
const fetchCategories = async () => {
  try {
    const response = await getCategories();
    categoryOptions.value = response.data || [];
  } catch (error) {
    console.error('获取商品分类失败:', error);
  }
};

// 重置查询参数
const resetQuery = () => {
  queryParams.name = '';
  queryParams.category = '';
  queryParams.status = '';
  page.value = 1;
  fetchData();
};

// 处理分页变化
const handleSizeChange = (val) => {
  limit.value = val;
  fetchData();
};

const handleCurrentChange = (val) => {
  page.value = val;
  fetchData();
};

// 多选变化
const handleSelectionChange = (selection) => {
  selectedProducts.value = selection;
};

// 新建商品
const handleCreate = () => {
  router.push('/product/create');
};

// 编辑商品
const handleEdit = (row) => {
  router.push(`/product/edit/${row.id}`);
};

// 切换商品状态（上架/下架）
const handleToggleStatus = async (row) => {
  try {
    const newStatus = row.status === 'active' ? 'inactive' : 'active';
    await updateProductStatus(row.id, newStatus);
    ElMessage.success(`商品${newStatus === 'active' ? '上架' : '下架'}成功`);
    
    // 更新本地数据
    row.status = newStatus;
  } catch (error) {
    console.error('更新商品状态失败:', error);
    ElMessage.error('操作失败');
  }
};

// 删除单个商品
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该商品吗？此操作不可逆', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteProduct(row.id);
      ElMessage.success('删除成功');
      fetchData();
    } catch (error) {
      console.error('删除商品失败:', error);
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

// 批量删除商品
const handleBatchDelete = () => {
  if (selectedProducts.value.length === 0) {
    ElMessage.warning('请先选择要删除的商品');
    return;
  }
  
  ElMessageBox.confirm(`确定要删除选中的 ${selectedProducts.value.length} 个商品吗？此操作不可逆`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const ids = selectedProducts.value.map(item => item.id);
      await batchDeleteProducts(ids);
      ElMessage.success('批量删除成功');
      fetchData();
    } catch (error) {
      console.error('批量删除失败:', error);
      ElMessage.error('批量删除失败');
    }
  }).catch(() => {});
};

onMounted(() => {
  fetchData();
  fetchCategories();
});
</script>

<style lang="scss" scoped>
.product-list {
  padding: 20px;

  .filter-container {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;

    .form-inline {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
    }

    .filter-item {
      width: 200px;
      margin-right: 10px;
    }
  }

  .action-container {
    margin-bottom: 20px;
  }

  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style> 