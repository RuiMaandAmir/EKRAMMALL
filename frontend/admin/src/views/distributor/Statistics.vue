<template>
  <div class="statistics-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="card-title">团队规模</div>
          <div class="card-content">
            <div class="stat-item">
              <span class="label">一级分销商</span>
              <span class="value">{{ statistics.team_stats.first_level }}</span>
            </div>
            <div class="stat-item">
              <span class="label">二级分销商</span>
              <span class="value">{{ statistics.team_stats.second_level }}</span>
            </div>
            <div class="stat-item">
              <span class="label">总人数</span>
              <span class="value">{{ statistics.team_stats.total }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="card-title">佣金统计</div>
          <div class="card-content">
            <div class="stat-item">
              <span class="label">总佣金</span>
              <span class="value">¥{{ statistics.commission_stats.total_commission }}</span>
            </div>
            <div class="stat-item">
              <span class="label">待结算</span>
              <span class="value">¥{{ statistics.commission_stats.pending_commission }}</span>
            </div>
            <div class="stat-item">
              <span class="label">已结算</span>
              <span class="value">¥{{ statistics.commission_stats.paid_commission }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="card-title">订单统计</div>
          <div class="card-content">
            <div class="stat-item">
              <span class="label">订单总数</span>
              <span class="value">{{ statistics.order_stats.total_orders }}</span>
            </div>
            <div class="stat-item">
              <span class="label">订单总额</span>
              <span class="value">¥{{ statistics.order_stats.total_amount }}</span>
            </div>
            <div class="stat-item">
              <span class="label">平均订单金额</span>
              <span class="value">¥{{ statistics.order_stats.average_order_amount }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="card-title">提现统计</div>
          <div class="card-content">
            <div class="stat-item">
              <span class="label">总提现</span>
              <span class="value">¥{{ statistics.withdrawal_stats.total_withdrawal }}</span>
            </div>
            <div class="stat-item">
              <span class="label">待处理</span>
              <span class="value">¥{{ statistics.withdrawal_stats.pending_withdrawal }}</span>
            </div>
            <div class="stat-item">
              <span class="label">已完成</span>
              <span class="value">¥{{ statistics.withdrawal_stats.completed_withdrawal }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { getDistributorStatistics } from '@/api/distributor'

export default {
  name: 'DistributorStatistics',
  data() {
    return {
      filterForm: {
        dateRange: []
      },
      statistics: {
        team_stats: {
          first_level: 0,
          second_level: 0,
          total: 0
        },
        commission_stats: {
          total_commission: 0,
          pending_commission: 0,
          paid_commission: 0
        },
        order_stats: {
          total_orders: 0,
          total_amount: 0,
          average_order_amount: 0
        },
        withdrawal_stats: {
          total_withdrawal: 0,
          pending_withdrawal: 0,
          completed_withdrawal: 0
        }
      }
    }
  },
  created() {
    this.fetchStatistics()
  },
  methods: {
    async fetchStatistics() {
      try {
        const params = {
          start_date: this.filterForm.dateRange[0],
          end_date: this.filterForm.dateRange[1]
        }
        const { data } = await getDistributorStatistics(params)
        this.statistics = data
      } catch (error) {
        this.$message.error('获取统计数据失败')
      }
    },
    handleSearch() {
      this.fetchStatistics()
    }
  }
}
</script>

<style lang="scss" scoped>
.statistics-container {
  padding: 20px;
  
  .filter-card {
    margin-bottom: 20px;
  }
  
  .statistics-row {
    margin-bottom: 20px;
  }
  
  .statistics-card {
    .card-title {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 15px;
    }
    
    .card-content {
      .stat-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        
        .label {
          color: #666;
        }
        
        .value {
          font-weight: bold;
          color: #409EFF;
        }
      }
    }
  }
}
</style> 