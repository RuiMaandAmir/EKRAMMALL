<template>
  <div class="promotion-list">
    <div class="filter-container">
      <el-form :inline="true" :model="queryParams" class="form-inline">
        <el-form-item label="活动名称">
          <el-input v-model="queryParams.name" placeholder="输入活动名称" clearable class="filter-item" />
        </el-form-item>
        <el-form-item label="活动状态">
          <el-select v-model="queryParams.status" placeholder="选择状态" clearable class="filter-item">
            <el-option label="全部" value="" />
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="ended" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="action-container">
      <el-button type="primary" @click="handleCreate">新建活动</el-button>
      <el-button type="success" @click="exportData">导出数据</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="name" label="活动名称" min-width="150" />
      <el-table-column prop="type" label="活动类型" width="120">
        <template #default="scope">
          {{ formatType(scope.row.type) }}
        </template>
      </el-table-column>
      <el-table-column prop="discount" label="折扣/优惠" width="120">
        <template #default="scope">
          {{ formatDiscount(scope.row) }}
        </template>
      </el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="160" />
      <el-table-column prop="end_time" label="结束时间" width="160" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="handleEdit(scope.row)"
          >编辑</el-button>
          <el-button 
            size="small" 
            type="success" 
            @click="handleProducts(scope.row)"
          >商品管理</el-button>
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
import { getActivities, deleteActivity, exportPromotionData } from '@/api/promotion';

const router = useRouter();
const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const page = ref(1);
const limit = ref(10);

const queryParams = reactive({
  name: '',
  status: '',
  page: 1,
  limit: 10
});

// 获取活动列表数据
const fetchData = async () => {
  loading.value = true;
  try {
    queryParams.page = page.value;
    queryParams.limit = limit.value;
    
    const response = await getActivities(queryParams);
    tableData.value = response.data.items || [];
    total.value = response.data.total || 0;
  } catch (error) {
    console.error('获取促销活动列表失败:', error);
    ElMessage.error('获取促销活动列表失败');
  } finally {
    loading.value = false;
  }
};

// 重置查询参数
const resetQuery = () => {
  queryParams.name = '';
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

// 新建活动
const handleCreate = () => {
  router.push('/promotion/create');
};

// 编辑活动
const handleEdit = (row) => {
  router.push(`/promotion/detail/${row.id}`);
};

// 商品管理
const handleProducts = (row) => {
  router.push(`/promotion/products/${row.id}`);
};

// 删除活动
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该活动吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteActivity(row.id);
      ElMessage.success('删除成功');
      fetchData();
    } catch (error) {
      console.error('删除活动失败:', error);
      ElMessage.error('删除活动失败');
    }
  }).catch(() => {});
};

// 导出数据
const exportData = async () => {
  try {
    await exportPromotionData(queryParams);
    ElMessage.success('数据导出成功');
  } catch (error) {
    console.error('导出数据失败:', error);
    ElMessage.error('导出数据失败');
  }
};

// 格式化活动类型
const formatType = (type) => {
  const typeMap = {
    'discount': '打折',
    'fixed_price': '固定价格',
    'cash_off': '满减'
  };
  return typeMap[type] || type;
};

// 格式化折扣/优惠
const formatDiscount = (row) => {
  if (row.type === 'discount') {
    return `${row.discount * 10}折`;
  } else if (row.type === 'fixed_price') {
    return `¥${row.fixed_price}`;
  } else if (row.type === 'cash_off') {
    return `满${row.threshold}减${row.cash_off}`;
  }
  return '';
};

// 格式化状态
const formatStatus = (status) => {
  const statusMap = {
    'pending': '未开始',
    'active': '进行中',
    'ended': '已结束'
  };
  return statusMap[status] || status;
};

// 获取状态标签类型
const getStatusType = (status) => {
  const typeMap = {
    'pending': 'info',
    'active': 'success',
    'ended': 'danger'
  };
  return typeMap[status] || '';
};

onMounted(() => {
  fetchData();
});
</script>

<style lang="scss" scoped>
.promotion-list {
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