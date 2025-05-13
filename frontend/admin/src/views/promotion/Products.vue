<template>
  <div class="promotion-products">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <span>促销活动商品管理</span>
            <el-tag class="ml-2" type="success" v-if="activityInfo.name">{{ activityInfo.name }}</el-tag>
          </div>
          <el-button @click="goBack">返回活动列表</el-button>
        </div>
      </template>
      
      <div class="toolbar">
        <el-button type="primary" @click="handleAddProducts">添加商品</el-button>
        <el-button type="danger" @click="handleBatchRemove" :disabled="selectedProducts.length === 0">
          批量移除
        </el-button>
      </div>
      
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%; margin-top: 15px;"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="商品ID" width="80" align="center" />
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
        <el-table-column prop="original_price" label="原价" width="100" align="right">
          <template #default="scope">
            ¥{{ scope.row.original_price }}
          </template>
        </el-table-column>
        <el-table-column prop="promotion_price" label="促销价" width="180">
          <template #default="scope">
            <el-input-number 
              v-if="scope.row.editing"
              v-model="scope.row.promotion_price"
              :min="0"
              :precision="2"
              size="small"
              style="width: 120px"
              @blur="savePromotionPrice(scope.row)"
            />
            <span v-else @click="enableEditing(scope.row)" class="editable-cell">
              ¥{{ scope.row.promotion_price }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="discount_rate" label="折扣率" width="100" align="center">
          <template #default="scope">
            {{ calculateDiscountRate(scope.row.original_price, scope.row.promotion_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" align="center" />
        <el-table-column prop="sales" label="销量" width="100" align="center" />
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button 
              size="small" 
              type="danger" 
              @click="handleRemove(scope.row)"
            >移除</el-button>
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
    </el-card>
    
    <!-- 添加商品对话框 -->
    <el-dialog 
      title="添加促销商品" 
      v-model="addProductsDialogVisible" 
      width="800px"
    >
      <div class="product-search">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品名称/编号"
          clearable
          @keyup.enter="searchProducts"
        >
          <template #append>
            <el-button @click="searchProducts">搜索</el-button>
          </template>
        </el-input>
      </div>
      
      <el-table
        v-loading="searchLoading"
        :data="searchResults"
        border
        style="width: 100%; margin-top: 15px;"
        @selection-change="handleSearchSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="商品ID" width="80" align="center" />
        <el-table-column label="商品图片" width="80" align="center">
          <template #default="scope">
            <el-image 
              :src="scope.row.image_url || '/placeholder-image.png'"
              style="width: 40px; height: 40px"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="price" label="原价" width="100" align="right">
          <template #default="scope">
            ¥{{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column label="促销价" width="180">
          <template #default="scope">
            <el-input-number 
              v-model="scope.row.promotion_price"
              :min="0"
              :precision="2"
              size="small"
              style="width: 120px"
            />
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" align="center" />
      </el-table>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addProductsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddProducts" :loading="addingProducts">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  getActivities, 
  getActivityProducts, 
  addActivityProduct, 
  updateActivityProduct, 
  removeActivityProduct
} from '@/api/promotion';
import { getProducts } from '@/api/product';

const router = useRouter();
const route = useRoute();
const activityId = route.params.activityId;

// 数据
const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const page = ref(1);
const limit = ref(10);
const activityInfo = ref({});
const selectedProducts = ref([]);

// 添加商品对话框相关
const addProductsDialogVisible = ref(false);
const searchKeyword = ref('');
const searchResults = ref([]);
const searchLoading = ref(false);
const selectedSearchProducts = ref([]);
const addingProducts = ref(false);

// 获取活动商品
const fetchData = async () => {
  loading.value = true;
  try {
    const response = await getActivityProducts(activityId);
    tableData.value = response.data.map(item => ({
      ...item,
      editing: false
    }));
    total.value = response.data.length || 0;
    
    // 获取活动信息
    const activityResponse = await getActivities({ id: activityId });
    activityInfo.value = activityResponse.data.items[0] || {};
  } catch (error) {
    console.error('获取活动商品失败:', error);
    ElMessage.error('获取活动商品失败');
  } finally {
    loading.value = false;
  }
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

// 搜索商品结果选择变化
const handleSearchSelectionChange = (selection) => {
  selectedSearchProducts.value = selection;
};

// 启用编辑模式
const enableEditing = (row) => {
  row.editing = true;
};

// 保存促销价
const savePromotionPrice = async (row) => {
  row.editing = false;
  try {
    await updateActivityProduct(activityId, row.id, {
      promotion_price: row.promotion_price
    });
    ElMessage.success('价格更新成功');
  } catch (error) {
    console.error('更新促销价失败:', error);
    ElMessage.error('更新促销价失败');
  }
};

// 计算折扣率
const calculateDiscountRate = (originalPrice, promotionPrice) => {
  if (!originalPrice || originalPrice <= 0) return '-';
  const rate = (promotionPrice / originalPrice * 10).toFixed(1);
  return `${rate}折`;
};

// 添加商品
const handleAddProducts = () => {
  searchKeyword.value = '';
  searchResults.value = [];
  selectedSearchProducts.value = [];
  addProductsDialogVisible.value = true;
};

// 搜索商品
const searchProducts = async () => {
  searchLoading.value = true;
  try {
    const response = await getProducts({
      query: searchKeyword.value,
      page: 1,
      limit: 50
    });
    
    searchResults.value = response.data.items.map(item => ({
      ...item,
      promotion_price: Math.round(item.price * 0.8 * 100) / 100 // 默认八折
    }));
  } catch (error) {
    console.error('搜索商品失败:', error);
    ElMessage.error('搜索商品失败');
  } finally {
    searchLoading.value = false;
  }
};

// 确认添加商品
const confirmAddProducts = async () => {
  if (selectedSearchProducts.value.length === 0) {
    ElMessage.warning('请选择要添加的商品');
    return;
  }
  
  addingProducts.value = true;
  
  try {
    const promises = selectedSearchProducts.value.map(product => {
      return addActivityProduct(activityId, {
        product_id: product.id,
        promotion_price: product.promotion_price
      });
    });
    
    await Promise.all(promises);
    ElMessage.success('商品添加成功');
    addProductsDialogVisible.value = false;
    fetchData(); // 刷新数据
  } catch (error) {
    console.error('添加商品失败:', error);
    ElMessage.error('添加商品失败');
  } finally {
    addingProducts.value = false;
  }
};

// 移除单个商品
const handleRemove = (row) => {
  ElMessageBox.confirm('确定要移除该商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await removeActivityProduct(activityId, row.id);
      ElMessage.success('商品移除成功');
      fetchData(); // 刷新数据
    } catch (error) {
      console.error('移除商品失败:', error);
      ElMessage.error('移除商品失败');
    }
  }).catch(() => {});
};

// 批量移除商品
const handleBatchRemove = () => {
  if (selectedProducts.value.length === 0) {
    ElMessage.warning('请先选择要移除的商品');
    return;
  }
  
  ElMessageBox.confirm(`确定要移除选中的 ${selectedProducts.value.length} 个商品吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const promises = selectedProducts.value.map(product => {
        return removeActivityProduct(activityId, product.id);
      });
      
      await Promise.all(promises);
      ElMessage.success('批量移除成功');
      fetchData(); // 刷新数据
    } catch (error) {
      console.error('批量移除失败:', error);
      ElMessage.error('批量移除失败');
    }
  }).catch(() => {});
};

// 返回活动列表
const goBack = () => {
  router.push('/promotion/list');
};

onMounted(() => {
  fetchData();
});
</script>

<style lang="scss" scoped>
.promotion-products {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .ml-2 {
      margin-left: 8px;
    }
  }
  
  .toolbar {
    margin-bottom: 15px;
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  
  .product-search {
    margin-bottom: 15px;
  }
  
  .editable-cell {
    cursor: pointer;
    color: #409EFF;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
</style> 