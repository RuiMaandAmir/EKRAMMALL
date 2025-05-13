<template>
  <div class="promotion-export">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据导出</span>
        </div>
      </template>
      
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="导出类型">
          <el-radio-group v-model="exportForm.type">
            <el-radio label="activities">促销活动</el-radio>
            <el-radio label="products">促销商品</el-radio>
            <el-radio label="statistics">销售统计</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="exportForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 350px;"
          />
        </el-form-item>
        
        <el-form-item v-if="exportForm.type === 'activities'" label="活动状态">
          <el-select v-model="exportForm.status" placeholder="选择状态" clearable style="width: 200px;">
            <el-option label="全部" value="" />
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="ended" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="exportForm.type === 'statistics'" label="统计维度">
          <el-checkbox-group v-model="exportForm.dimensions">
            <el-checkbox label="daily">日维度</el-checkbox>
            <el-checkbox label="weekly">周维度</el-checkbox>
            <el-checkbox label="monthly">月维度</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleExport" :loading="exporting">
            {{ exporting ? '导出中...' : '开始导出' }}
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="tips-section">
        <h3>导出说明：</h3>
        <ul>
          <li><strong>促销活动：</strong> 导出所有促销活动的基本信息，包括活动名称、类型、时间、状态等。</li>
          <li><strong>促销商品：</strong> 导出参与促销的商品信息，包括商品名称、原价、促销价、销量等。</li>
          <li><strong>销售统计：</strong> 导出促销活动的销售数据统计，包括销售额、订单数、客单价等。</li>
        </ul>
        <el-alert
          title="数据导出文件将以Excel格式下载到您的设备上"
          type="info"
          show-icon
        />
      </div>
      
      <div v-if="exportHistory.length > 0" class="history-section">
        <h3>最近导出记录：</h3>
        <el-table :data="exportHistory" border style="width: 100%;">
          <el-table-column prop="time" label="导出时间" width="180" />
          <el-table-column prop="type" label="导出类型" width="120">
            <template #default="scope">
              {{ formatExportType(scope.row.type) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                {{ scope.row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="fileName" label="文件名" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { exportPromotionData, exportPromotionStats } from '@/api/promotion';

// 导出表单
const exportForm = reactive({
  type: 'activities',
  dateRange: [],
  status: '',
  dimensions: ['daily', 'monthly']
});

const exporting = ref(false);
const exportHistory = ref([]);

// 格式化导出类型
const formatExportType = (type) => {
  const typeMap = {
    'activities': '促销活动',
    'products': '促销商品',
    'statistics': '销售统计'
  };
  return typeMap[type] || type;
};

// 处理导出
const handleExport = async () => {
  if (!exportForm.dateRange || exportForm.dateRange.length !== 2) {
    ElMessage.warning('请选择时间范围');
    return;
  }
  
  exporting.value = true;
  
  try {
    const params = {
      start_date: exportForm.dateRange[0],
      end_date: exportForm.dateRange[1],
      type: exportForm.type
    };
    
    if (exportForm.type === 'activities' && exportForm.status) {
      params.status = exportForm.status;
    }
    
    if (exportForm.type === 'statistics' && exportForm.dimensions.length > 0) {
      params.dimensions = exportForm.dimensions.join(',');
    }
    
    let response;
    if (exportForm.type === 'statistics') {
      response = await exportPromotionStats(params);
    } else {
      response = await exportPromotionData(params);
    }
    
    // 处理文件下载
    const blob = new Blob([response], { type: 'application/vnd.ms-excel' });
    const fileName = `促销数据_${new Date().toLocaleDateString()}.xlsx`;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
    URL.revokeObjectURL(link.href);
    
    // 添加到导出历史
    exportHistory.value.unshift({
      time: new Date().toLocaleString(),
      type: exportForm.type,
      status: 'success',
      fileName: fileName
    });
    
    ElMessage.success('数据导出成功');
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('数据导出失败');
    
    // 添加失败记录到历史
    exportHistory.value.unshift({
      time: new Date().toLocaleString(),
      type: exportForm.type,
      status: 'failed',
      fileName: '导出失败'
    });
  } finally {
    exporting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  exportForm.type = 'activities';
  exportForm.dateRange = [];
  exportForm.status = '';
  exportForm.dimensions = ['daily', 'monthly'];
};
</script>

<style lang="scss" scoped>
.promotion-export {
  padding: 20px;
  
  .card-header {
    font-weight: bold;
  }
  
  .tips-section {
    margin-top: 20px;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    h3 {
      margin-top: 0;
      margin-bottom: 10px;
      font-size: 16px;
      color: #303133;
    }
    
    ul {
      padding-left: 20px;
      margin-bottom: 15px;
      
      li {
        line-height: 1.8;
        color: #606266;
      }
    }
  }
  
  .history-section {
    margin-top: 30px;
    
    h3 {
      margin-bottom: 15px;
      font-size: 16px;
      color: #303133;
    }
  }
}
</style> 