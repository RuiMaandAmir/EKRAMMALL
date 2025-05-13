<template>
  <div class="app-container">
    <div class="filter-container">
      <el-form :inline="true" :model="listQuery" class="demo-form-inline">
        <el-form-item label="用户名">
          <el-input v-model="listQuery.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="listQuery.phone" placeholder="手机号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="listQuery.status" placeholder="选择状态" clearable>
            <el-option label="启用" value="true" />
            <el-option label="禁用" value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="注册时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            align="right"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="handleExport">导出用户</el-button>
        </el-form-item>
      </el-form>
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
      <el-table-column label="用户名" width="150">
        <template #default="scope">
          <span class="link-type" @click="handleDetail(scope.row)">{{ scope.row.username }}</span>
        </template>
      </el-table-column>
      <el-table-column label="手机号" width="120" align="center">
        <template #default="scope">
          <span>{{ scope.row.phone }}</span>
        </template>
      </el-table-column>
      <el-table-column label="性别" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.gender === 'M' ? '男' : scope.row.gender === 'F' ? '女' : '未知' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="订单数" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.order_count }}</span>
        </template>
      </el-table-column>
      <el-table-column label="消费金额" width="120" align="center">
        <template #default="scope">
          <span>¥{{ scope.row.total_amount.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            @change="(val) => handleStatusChange(scope.row, val)"
          />
        </template>
      </el-table-column>
      <el-table-column label="注册时间" width="150" align="center">
        <template #default="scope">
          <span>{{ formatDate(scope.row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="180" align="center">
        <template #default="scope">
          <el-button size="small" type="primary" @click="handleDetail(scope.row)">查看</el-button>
          <el-button size="small" type="success" @click="handleOrders(scope.row)">订单</el-button>
          <el-button size="small" type="info" @click="handleAddresses(scope.row)">地址</el-button>
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

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="600px"
    >
      <el-descriptions column="2" border>
        <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentUser.phone }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentUser.email || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ currentUser.gender === 'M' ? '男' : currentUser.gender === 'F' ? '女' : '未知' }}</el-descriptions-item>
        <el-descriptions-item label="生日">{{ currentUser.birthday || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatDate(currentUser.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ formatDate(currentUser.last_login_at) }}</el-descriptions-item>
        <el-descriptions-item label="订单数">{{ currentUser.order_count }}</el-descriptions-item>
        <el-descriptions-item label="消费金额">¥{{ currentUser.total_amount ? currentUser.total_amount.toFixed(2) : '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.status ? 'success' : 'danger'">{{ currentUser.status ? '正常' : '禁用' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentUser.note || '无' }}</el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleEdit(currentUser)">编辑</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 用户编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" disabled></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email"></el-input>
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="userForm.gender" placeholder="请选择性别">
            <el-option label="男" value="M"></el-option>
            <el-option label="女" value="F"></el-option>
            <el-option label="未知" value=""></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="生日" prop="birthday">
          <el-date-picker v-model="userForm.birthday" type="date" value-format="YYYY-MM-DD"></el-date-picker>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="userForm.status"></el-switch>
        </el-form-item>
        <el-form-item label="备注" prop="note">
          <el-input v-model="userForm.note" type="textarea" :rows="3" placeholder="请输入备注"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 用户订单对话框 -->
    <el-dialog
      v-model="ordersDialogVisible"
      title="用户订单"
      width="900px"
    >
      <div v-loading="ordersLoading">
        <el-table :data="userOrders" border style="width: 100%">
          <el-table-column prop="order_number" label="订单号" width="180"></el-table-column>
          <el-table-column prop="total_amount" label="金额" width="100">
            <template #default="scope">
              <span>¥{{ scope.row.total_amount.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getOrderStatusType(scope.row.status)">{{ getOrderStatusName(scope.row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="下单时间" width="150">
            <template #default="scope">
              <span>{{ formatDate(scope.row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewOrder(scope.row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container" v-if="userOrders.length > 0">
          <el-pagination
            v-model:current-page="ordersQuery.page"
            v-model:page-size="ordersQuery.limit"
            :page-sizes="[5, 10, 20]"
            layout="total, sizes, prev, pager, next"
            :total="ordersTotal"
            @size-change="handleOrdersSizeChange"
            @current-change="handleOrdersCurrentChange"
          />
        </div>
        
        <div v-if="userOrders.length === 0" class="no-data">该用户暂无订单</div>
      </div>
    </el-dialog>

    <!-- 用户地址对话框 -->
    <el-dialog
      v-model="addressesDialogVisible"
      title="用户地址"
      width="700px"
    >
      <div v-loading="addressesLoading">
        <el-table :data="userAddresses" border style="width: 100%">
          <el-table-column prop="name" label="收货人" width="100"></el-table-column>
          <el-table-column prop="phone" label="联系电话" width="120"></el-table-column>
          <el-table-column prop="address" label="地址" min-width="200"></el-table-column>
          <el-table-column prop="is_default" label="默认" width="80">
            <template #default="scope">
              <el-tag v-if="scope.row.is_default" type="success">默认</el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="userAddresses.length === 0" class="no-data">该用户暂无地址</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { 
  getCustomerList, 
  getCustomerDetail, 
  updateCustomer, 
  updateCustomerStatus,
  getCustomerOrders,
  getCustomerAddresses,
  exportCustomers
} from '@/api/user';

const router = useRouter();

// 列表数据
const list = ref([]);
const total = ref(0);
const listLoading = ref(false);

// 查询条件
const listQuery = reactive({
  page: 1,
  limit: 20,
  username: '',
  phone: '',
  status: '',
  start_date: '',
  end_date: ''
});

// 日期范围
const dateRange = ref([]);

// 对话框控制
const detailDialogVisible = ref(false);
const editDialogVisible = ref(false);
const ordersDialogVisible = ref(false);
const addressesDialogVisible = ref(false);

// 加载状态
const ordersLoading = ref(false);
const addressesLoading = ref(false);

// 当前用户
const currentUser = ref({});
const userOrders = ref([]);
const userAddresses = ref([]);
const ordersTotal = ref(0);

// 用户订单查询
const ordersQuery = reactive({
  page: 1,
  limit: 10
});

// 编辑表单
const userFormRef = ref(null);
const userForm = reactive({
  id: '',
  username: '',
  phone: '',
  email: '',
  gender: '',
  birthday: '',
  status: true,
  note: ''
});

// 表单验证规则
const userRules = {
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};

// 初始化
onMounted(() => {
  fetchUsers();
});

// 监听日期范围变化，更新查询条件
const updateDateRange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    listQuery.start_date = dateRange.value[0];
    listQuery.end_date = dateRange.value[1];
  } else {
    listQuery.start_date = '';
    listQuery.end_date = '';
  }
};

// 获取用户列表
const fetchUsers = async () => {
  updateDateRange();
  listLoading.value = true;
  try {
    const res = await getCustomerList(listQuery);
    list.value = res.data.items;
    total.value = res.data.total;
  } catch (error) {
    console.error('获取用户列表失败:', error);
  } finally {
    listLoading.value = false;
  }
};

// 筛选
const handleFilter = () => {
  listQuery.page = 1;
  fetchUsers();
};

// 重置筛选
const resetFilter = () => {
  listQuery.username = '';
  listQuery.phone = '';
  listQuery.status = '';
  dateRange.value = [];
  listQuery.start_date = '';
  listQuery.end_date = '';
  handleFilter();
};

// 分页
const handleSizeChange = (val) => {
  listQuery.limit = val;
  fetchUsers();
};

const handleCurrentChange = (val) => {
  listQuery.page = val;
  fetchUsers();
};

// 导出用户
const handleExport = async () => {
  updateDateRange();
  try {
    ElMessage.info('正在导出用户数据，请稍候...');
    const res = await exportCustomers(listQuery);
    
    // 创建Blob并下载
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const fileName = `用户数据_${new Date().toISOString().split('T')[0]}.xlsx`;
    
    if (window.navigator.msSaveOrOpenBlob) {
      // IE
      window.navigator.msSaveOrOpenBlob(blob, fileName);
    } else {
      // 其他浏览器
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = fileName;
      link.click();
      window.URL.revokeObjectURL(link.href);
    }
    
    ElMessage.success('用户导出成功');
  } catch (error) {
    console.error('导出用户失败:', error);
    ElMessage.error('导出用户失败');
  }
};

// 查看用户详情
const handleDetail = async (row) => {
  try {
    const res = await getCustomerDetail(row.id);
    currentUser.value = res.data;
    detailDialogVisible.value = true;
  } catch (error) {
    console.error('获取用户详情失败:', error);
    ElMessage.error('获取用户详情失败');
  }
};

// 编辑用户
const handleEdit = (user) => {
  Object.assign(userForm, {
    id: user.id,
    username: user.username,
    phone: user.phone,
    email: user.email,
    gender: user.gender,
    birthday: user.birthday,
    status: user.status,
    note: user.note
  });
  
  detailDialogVisible.value = false;
  editDialogVisible.value = true;
};

// 提交用户表单
const submitUserForm = () => {
  userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await updateCustomer(userForm.id, userForm);
        ElMessage.success('更新成功');
        editDialogVisible.value = false;
        
        // 刷新用户列表
        fetchUsers();
        
        // 如果详情对话框还打开着，刷新详情
        if (currentUser.value.id === userForm.id) {
          handleDetail({ id: userForm.id });
        }
      } catch (error) {
        console.error('更新用户失败:', error);
        ElMessage.error('更新用户失败');
      }
    } else {
      return false;
    }
  });
};

// 更新用户状态
const handleStatusChange = async (row, status) => {
  try {
    await updateCustomerStatus(row.id, status);
    ElMessage.success(`用户已${status ? '启用' : '禁用'}`);
  } catch (error) {
    console.error('更新用户状态失败:', error);
    ElMessage.error('更新状态失败');
    // 恢复状态
    row.status = !status;
  }
};

// 查看用户订单
const handleOrders = async (row) => {
  ordersQuery.page = 1;
  ordersQuery.limit = 10;
  ordersLoading.value = true;
  ordersDialogVisible.value = true;
  
  try {
    const res = await getCustomerOrders(row.id, ordersQuery);
    userOrders.value = res.data.items;
    ordersTotal.value = res.data.total;
  } catch (error) {
    console.error('获取用户订单失败:', error);
    ElMessage.error('获取用户订单失败');
  } finally {
    ordersLoading.value = false;
  }
};

// 订单分页
const handleOrdersSizeChange = async (val) => {
  ordersQuery.limit = val;
  ordersLoading.value = true;
  
  try {
    const res = await getCustomerOrders(currentUser.value.id, ordersQuery);
    userOrders.value = res.data.items;
    ordersTotal.value = res.data.total;
  } catch (error) {
    console.error('获取用户订单失败:', error);
  } finally {
    ordersLoading.value = false;
  }
};

const handleOrdersCurrentChange = async (val) => {
  ordersQuery.page = val;
  ordersLoading.value = true;
  
  try {
    const res = await getCustomerOrders(currentUser.value.id, ordersQuery);
    userOrders.value = res.data.items;
    ordersTotal.value = res.data.total;
  } catch (error) {
    console.error('获取用户订单失败:', error);
  } finally {
    ordersLoading.value = false;
  }
};

// 查看订单详情
const viewOrder = (order) => {
  router.push({ path: '/orders', query: { order_number: order.order_number } });
};

// 查看用户地址
const handleAddresses = async (row) => {
  addressesLoading.value = true;
  addressesDialogVisible.value = true;
  
  try {
    const res = await getCustomerAddresses(row.id);
    userAddresses.value = res.data;
  } catch (error) {
    console.error('获取用户地址失败:', error);
    ElMessage.error('获取用户地址失败');
  } finally {
    addressesLoading.value = false;
  }
};

// 获取订单状态名称
const getOrderStatusName = (status) => {
  const statusMap = {
    'PENDING': '待确认',
    'CONFIRMED': '已确认',
    'SHIPPED': '已发货',
    'COMPLETED': '已完成',
    'CANCELLED': '已取消',
    'REFUNDED': '已退款'
  };
  return statusMap[status] || status;
};

// 获取订单状态类型（用于标签颜色）
const getOrderStatusType = (status) => {
  const statusMap = {
    'PENDING': 'warning',
    'CONFIRMED': 'info',
    'SHIPPED': 'primary',
    'COMPLETED': 'success',
    'CANCELLED': 'danger',
    'REFUNDED': 'danger'
  };
  return statusMap[status] || '';
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

.no-data {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}
</style> 