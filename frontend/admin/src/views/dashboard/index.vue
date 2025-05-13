<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>欢迎使用伊客拉穆商城管理系统</h1>
      <p>今天是 {{ currentDate }}</p>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>总订单数</span>
            </div>
          </template>
          <div class="card-value">0</div>
          <div class="card-footer">今日订单: 0</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>总销售额</span>
            </div>
          </template>
          <div class="card-value">¥0.00</div>
          <div class="card-footer">今日销售: ¥0.00</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>用户数量</span>
            </div>
          </template>
          <div class="card-value">0</div>
          <div class="card-footer">今日新增: 0</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>商品数量</span>
            </div>
          </template>
          <div class="card-value">0</div>
          <div class="card-footer">已上架: 0</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近一周销售趋势</span>
            </div>
          </template>
          <div class="placeholder-chart">
            <p>数据加载中...</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>商品销售排行</span>
            </div>
          </template>
          <ul class="ranking-list">
            <li class="no-data">暂无数据</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// 获取当前日期
const currentDate = ref(new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
}));

onMounted(() => {
  // 在实际项目中，这里可以加载统计数据
  console.log('Dashboard mounted');
});
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 20px;
  
  h1 {
    font-size: 24px;
    color: #303133;
    margin: 0 0 10px 0;
  }
  
  p {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.data-card {
  height: 150px;
  margin-bottom: 20px;
  
  .card-value {
    font-size: 28px;
    font-weight: bold;
    color: #4caf50;
    margin: 15px 0;
  }
  
  .card-footer {
    font-size: 14px;
    color: #909399;
  }
}

.chart-card {
  height: 350px;
  margin-bottom: 20px;
}

.placeholder-chart {
  height: 280px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.ranking-list {
  padding: 0;
  list-style: none;
  
  .no-data {
    height: 280px;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f5f7fa;
    border-radius: 4px;
  }
}

.mt-20 {
  margin-top: 20px;
}
</style> 