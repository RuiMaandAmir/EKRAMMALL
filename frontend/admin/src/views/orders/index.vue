<template>
  <div class="app-container">
    <div class="filter-container">
      <el-form :inline="true" :model="listQuery" class="demo-form-inline">
        <el-form-item label="订单号">
          <el-input v-model="listQuery.order_number" placeholder="订单号" clearable />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="listQuery.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="listQuery.status" placeholder="选择状态" clearable>
            <el-option v-for="item in orderStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="下单时间">
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
          <el-button type="success" @click="handleExport">导出订单</el-button>
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
      <el-table-column align="center" label="订单号" width="180">
        <template #default="scope">
          <span class="link-type" @click="handleDetail(scope.row)">{{ scope.row.order_number }}</span>
        </template>
      </el-table-column>
      <el-table-column label="用户信息" width="150">
        <template #default="scope">
          <div>{{ scope.row.username }}</div>
          <div style="font-size: 12px; color: #999">{{ scope.row.phone }}</div>
        </template>
      </el-table-column>
      <el-table-column label="金额" width="100" align="center">
        <template #default="scope">
          <span>¥{{ scope.row.total_amount.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="支付方式" width="120" align="center">
        <template #default="scope">
          <el-tag size="small">{{ getPaymentMethodName(scope.row.payment_method) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="订单状态" width="120" align="center">
        <template #default="scope">
          <el-tag :type="getOrderStatusType(scope.row.status)">{{ getOrderStatusName(scope.row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="下单时间" width="160" align="center">
        <template #default="scope">
          <span>{{ formatDate(scope.row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="220" align="center">
        <template #default="scope">
          <el-button size="small" @click="handleDetail(scope.row)">查看</el-button>
          <el-button 
            v-if="scope.row.status === 'PENDING'" 
            size="small" 
            type="success" 
            @click="handleConfirm(scope.row)"
          >确认</el-button>
          <el-button 
            v-if="scope.row.status === 'CONFIRMED'" 
            size="small" 
            type="primary" 
            @click="handleShip(scope.row)"
          >发货</el-button>
          <el-button 
            v-if="['PENDING', 'CONFIRMED'].includes(scope.row.status)" 
            size="small" 
            type="danger" 
            @click="handleCancel(scope.row)"
          >取消</el-button>
          <el-button 
            v-if="scope.row.status === 'SHIPPED'" 
            size="small" 
            type="info" 
            @click="handleViewShipping(scope.row)"
          >物流</el-button>
          <el-button 
            v-if="scope.row.status === 'SHIPPED'" 
            size="small" 
            type="success" 
            @click="handleComplete(scope.row)"
          >完成</el-button>
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

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="订单详情"
      width="800px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单编号" :span="2">{{ currentOrder.order_number }}</el-descriptions-item>
        <el-descriptions-item label="订单状态" :span="1">
          <el-tag :type="getOrderStatusType(currentOrder.status)">{{ getOrderStatusName(currentOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="下单时间" :span="1">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="用户姓名" :span="1">{{ currentOrder.username }}</el-descriptions-item>
        <el-descriptions-item label="联系电话" :span="1">{{ currentOrder.phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ currentOrder.address }}</el-descriptions-item>
        <el-descriptions-item label="支付方式" :span="1">{{ getPaymentMethodName(currentOrder.payment_method) }}</el-descriptions-item>
        <el-descriptions-item label="支付时间" :span="1">{{ formatDate(currentOrder.paid_at) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.note || '无' }}</el-descriptions-item>
      </el-descriptions>

      <div class="order-products-title">商品信息</div>
      <el-table :data="currentOrder.items || []" border style="width: 100%; margin-top: 15px;">
        <el-table-column label="商品图片" width="80" align="center">
          <template #default="scope">
            <el-image 
              style="width: 50px; height: 50px" 
              :src="scope.row.product_image" 
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
        <el-table-column label="商品名称" min-width="180">
          <template #default="scope">
            <span>{{ scope.row.product_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="规格" width="100">
          <template #default="scope">
            <span>{{ scope.row.sku_name || '默认' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单价" width="100" align="center">
          <template #default="scope">
            <span>¥{{ scope.row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="80" align="center">
          <template #default="scope">
            <span>{{ scope.row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column label="小计" width="120" align="center">
          <template #default="scope">
            <span>¥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="order-amount">
        <p>商品金额：¥{{ currentOrder.items_amount ? currentOrder.items_amount.toFixed(2) : '0.00' }}</p>
        <p>运费：¥{{ currentOrder.shipping_fee ? currentOrder.shipping_fee.toFixed(2) : '0.00' }}</p>
        <p>优惠：- ¥{{ currentOrder.discount ? currentOrder.discount.toFixed(2) : '0.00' }}</p>
        <p class="total-amount">订单总额：¥{{ currentOrder.total_amount ? currentOrder.total_amount.toFixed(2) : '0.00' }}</p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button 
            v-if="currentOrder.status === 'PENDING'" 
            type="success" 
            @click="handleConfirm(currentOrder)"
          >确认订单</el-button>
          <el-button 
            v-if="currentOrder.status === 'CONFIRMED'" 
            type="primary" 
            @click="handleShip(currentOrder)"
          >发货</el-button>
          <el-button 
            v-if="['PENDING', 'CONFIRMED'].includes(currentOrder.status)" 
            type="danger" 
            @click="handleCancel(currentOrder)"
          >取消订单</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 发货对话框 -->
    <el-dialog
      v-model="shipDialogVisible"
      title="订单发货"
      width="500px"
    >
      <el-form
        ref="shipFormRef"
        :model="shipForm"
        :rules="shipRules"
        label-width="100px"
      >
        <el-form-item label="物流公司" prop="shipping_company">
          <el-select v-model="shipForm.shipping_company" placeholder="选择物流公司">
            <el-option label="顺丰速运" value="SF" />
            <el-option label="中通快递" value="ZTO" />
            <el-option label="圆通速递" value="YTO" />
            <el-option label="韵达速递" value="YD" />
            <el-option label="申通快递" value="STO" />
            <el-option label="邮政EMS" value="EMS" />
          </el-select>
        </el-form-item>
        <el-form-item label="物流单号" prop="tracking_number">
          <el-input v-model="shipForm.tracking_number" placeholder="请输入物流单号" />
        </el-form-item>
        <el-form-item label="发货备注" prop="note">
          <el-input v-model="shipForm.note" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="shipDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitShipForm">确定发货</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 取消订单对话框 -->
    <el-dialog
      v-model="cancelDialogVisible"
      title="取消订单"
      width="500px"
    >
      <el-form
        ref="cancelFormRef"
        :model="cancelForm"
        :rules="cancelRules"
        label-width="100px"
      >
        <el-form-item label="取消原因" prop="reason">
          <el-select v-model="cancelForm.reason" placeholder="选择取消原因">
            <el-option label="用户取消" value="用户取消" />
            <el-option label="商品缺货" value="商品缺货" />
            <el-option label="重新拍单" value="重新拍单" />
            <el-option label="其他原因" value="其他原因" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="note">
          <el-input v-model="cancelForm.note" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelDialogVisible = false">关闭</el-button>
          <el-button type="danger" @click="submitCancelForm">确定取消</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 物流信息对话框 -->
    <el-dialog
      v-model="shippingDialogVisible"
      title="物流信息"
      width="600px"
    >
      <div v-loading="shippingLoading">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="物流公司">{{ getShippingCompanyName(shippingInfo.shipping_company) }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ shippingInfo.tracking_number }}</el-descriptions-item>
          <el-descriptions-item label="发货时间">{{ formatDate(shippingInfo.shipped_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="shipping-timeline">
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in shippingInfo.tracking || []"
              :key="index"
              :timestamp="activity.time"
              :type="index === 0 ? 'primary' : ''"
            >
              {{ activity.context }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { PictureFilled } from '@element-plus/icons-vue';
import { 
  getOrders, 
  getOrderDetail, 
  confirmOrder, 
  shipOrder, 
  cancelOrder, 
  completeOrder,
  getShippingInfo,
  exportOrders
} from '@/api/order';

// 列表数据
const list = ref([]);
const total = ref(0);
const listLoading = ref(false);

// 订单状态选项
const orderStatusOptions = [
  { label: '待确认', value: 'PENDING' },
  { label: '已确认', value: 'CONFIRMED' },
  { label: '已发货', value: 'SHIPPED' },
  { label: '已完成', value: 'COMPLETED' },
  { label: '已取消', value: 'CANCELLED' },
  { label: '已退款', value: 'REFUNDED' }
];

// 查询条件
const listQuery = reactive({
  page: 1,
  limit: 20,
  order_number: '',
  username: '',
  status: '',
  start_date: '',
  end_date: ''
});

// 日期范围
const dateRange = ref([]);

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

// 对话框控制
const detailDialogVisible = ref(false);
const shipDialogVisible = ref(false);
const cancelDialogVisible = ref(false);
const shippingDialogVisible = ref(false);
const shippingLoading = ref(false);

// 表单引用
const shipFormRef = ref(null);
const cancelFormRef = ref(null);

// 当前操作的订单
const currentOrder = ref({});
const shippingInfo = ref({});

// 发货表单
const shipForm = reactive({
  orderId: '',
  shipping_company: '',
  tracking_number: '',
  note: ''
});

// 发货表单验证规则
const shipRules = {
  shipping_company: [
    { required: true, message: '请选择物流公司', trigger: 'change' }
  ],
  tracking_number: [
    { required: true, message: '请输入物流单号', trigger: 'blur' },
    { min: 5, max: 30, message: '长度在 5 到 30 个字符', trigger: 'blur' }
  ]
};

// 取消订单表单
const cancelForm = reactive({
  orderId: '',
  reason: '',
  note: ''
});

// 取消订单表单验证规则
const cancelRules = {
  reason: [
    { required: true, message: '请选择取消原因', trigger: 'change' }
  ]
};

// 初始化
onMounted(() => {
  fetchOrders();
});

// 获取订单列表
const fetchOrders = async () => {
  updateDateRange();
  listLoading.value = true;
  try {
    const res = await getOrders(listQuery);
    list.value = res.data.items;
    total.value = res.data.total;
  } catch (error) {
    console.error('获取订单列表失败:', error);
  } finally {
    listLoading.value = false;
  }
};

// 筛选
const handleFilter = () => {
  listQuery.page = 1;
  fetchOrders();
};

// 重置筛选
const resetFilter = () => {
  listQuery.order_number = '';
  listQuery.username = '';
  listQuery.status = '';
  dateRange.value = [];
  listQuery.start_date = '';
  listQuery.end_date = '';
  handleFilter();
};

// 分页
const handleSizeChange = (val) => {
  listQuery.limit = val;
  fetchOrders();
};

const handleCurrentChange = (val) => {
  listQuery.page = val;
  fetchOrders();
};

// 导出订单
const handleExport = async () => {
  updateDateRange();
  try {
    ElMessage.info('正在导出订单数据，请稍候...');
    const res = await exportOrders(listQuery);
    
    // 创建Blob并下载
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const fileName = `订单数据_${new Date().toISOString().split('T')[0]}.xlsx`;
    
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
    
    ElMessage.success('订单导出成功');
  } catch (error) {
    console.error('导出订单失败:', error);
    ElMessage.error('导出订单失败');
  }
};

// 查看订单详情
const handleDetail = async (row) => {
  currentOrder.value = { ...row };
  
  // 如果需要加载更详细的信息
  try {
    const res = await getOrderDetail(row.id);
    currentOrder.value = res.data;
  } catch (error) {
    console.error('获取订单详情失败:', error);
  }
  
  detailDialogVisible.value = true;
};

// 确认订单
const handleConfirm = (row) => {
  ElMessageBox.confirm(
    `确认订单 "${row.order_number}"?`, 
    '确认订单', 
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    try {
      await confirmOrder(row.id);
      ElMessage.success('订单已确认');
      fetchOrders();
      if (detailDialogVisible.value) {
        handleDetail(row);
      }
    } catch (error) {
      console.error('确认订单失败:', error);
      ElMessage.error('确认订单失败');
    }
  }).catch(() => {});
};

// 发货
const handleShip = (row) => {
  shipForm.orderId = row.id;
  shipForm.shipping_company = '';
  shipForm.tracking_number = '';
  shipForm.note = '';
  shipDialogVisible.value = true;
};

// 提交发货表单
const submitShipForm = () => {
  shipFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await shipOrder(shipForm.orderId, {
          shipping_company: shipForm.shipping_company,
          tracking_number: shipForm.tracking_number,
          note: shipForm.note
        });
        ElMessage.success('发货成功');
        shipDialogVisible.value = false;
        fetchOrders();
        if (detailDialogVisible.value) {
          handleDetail({ id: shipForm.orderId });
        }
      } catch (error) {
        console.error('发货失败:', error);
        ElMessage.error('发货失败');
      }
    } else {
      return false;
    }
  });
};

// 取消订单
const handleCancel = (row) => {
  cancelForm.orderId = row.id;
  cancelForm.reason = '';
  cancelForm.note = '';
  cancelDialogVisible.value = true;
};

// 提交取消订单表单
const submitCancelForm = () => {
  cancelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await cancelOrder(cancelForm.orderId, cancelForm.reason + (cancelForm.note ? ': ' + cancelForm.note : ''));
        ElMessage.success('订单已取消');
        cancelDialogVisible.value = false;
        fetchOrders();
        if (detailDialogVisible.value) {
          detailDialogVisible.value = false;
        }
      } catch (error) {
        console.error('取消订单失败:', error);
        ElMessage.error('取消订单失败');
      }
    } else {
      return false;
    }
  });
};

// 完成订单
const handleComplete = (row) => {
  ElMessageBox.confirm(
    `确认将订单 "${row.order_number}" 标记为已完成?`, 
    '完成订单', 
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(async () => {
    try {
      await completeOrder(row.id);
      ElMessage.success('订单已完成');
      fetchOrders();
      if (detailDialogVisible.value) {
        handleDetail(row);
      }
    } catch (error) {
      console.error('完成订单失败:', error);
      ElMessage.error('完成订单失败');
    }
  }).catch(() => {});
};

// 查看物流信息
const handleViewShipping = async (row) => {
  shippingLoading.value = true;
  shippingInfo.value = {};
  shippingDialogVisible.value = true;
  
  try {
    const res = await getShippingInfo(row.id);
    shippingInfo.value = res.data;
  } catch (error) {
    console.error('获取物流信息失败:', error);
    ElMessage.error('获取物流信息失败');
  } finally {
    shippingLoading.value = false;
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

// 获取支付方式名称
const getPaymentMethodName = (method) => {
  const methodMap = {
    'WECHAT': '微信支付',
    'ALIPAY': '支付宝',
    'COD': '货到付款',
    'BANK_TRANSFER': '银行转账'
  };
  return methodMap[method] || method;
};

// 获取物流公司名称
const getShippingCompanyName = (code) => {
  const companyMap = {
    'SF': '顺丰速运',
    'ZTO': '中通快递',
    'YTO': '圆通速递',
    'YD': '韵达速递',
    'STO': '申通快递',
    'EMS': '邮政EMS'
  };
  return companyMap[code] || code;
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

.order-products-title {
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.order-amount {
  margin-top: 20px;
  text-align: right;
  
  p {
    margin: 5px 0;
  }
  
  .total-amount {
    font-size: 16px;
    font-weight: bold;
    color: #f56c6c;
  }
}

.shipping-timeline {
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.image-error {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
}
</style> 