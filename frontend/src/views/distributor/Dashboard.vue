<template>
  <div class="distributor-dashboard">
    <!-- 数据概览 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">总销售额</div>
            <div class="data-value">¥{{ distributorInfo.total_sales }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">总佣金</div>
            <div class="data-value">¥{{ distributorInfo.total_commission }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">可提现佣金</div>
            <div class="data-value">¥{{ distributorInfo.available_commission }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">团队人数</div>
            <div class="data-value">{{ teamStats.total_members }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分销链接统计 -->
    <el-card class="mt-20">
      <div slot="header">
        <span>分销链接统计</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-title">总点击次数</div>
            <div class="stat-value">{{ linkStats.total_clicks }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-title">总订单数</div>
            <div class="stat-value">{{ linkStats.total_orders }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-title">总佣金</div>
            <div class="stat-value">¥{{ linkStats.total_commission }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近佣金记录 -->
    <el-card class="mt-20">
      <div slot="header">
        <span>最近佣金记录</span>
        <el-button
          style="float: right; padding: 3px 0"
          type="text"
          @click="$router.push('/distributor/commissions')"
        >
          查看更多
        </el-button>
      </div>
      <el-table :data="recentCommissions" style="width: 100%">
        <el-table-column prop="order_number" label="订单号" width="180" />
        <el-table-column prop="amount" label="佣金金额" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.amount }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="分销层级" width="100">
          <template slot-scope="scope">
            {{ scope.row.level === 1 ? '一级' : '二级' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'DistributorDashboard',
  data() {
    return {
      linkStats: {
        total_clicks: 0,
        total_orders: 0,
        total_commission: 0
      },
      teamStats: {
        total_members: 0
      },
      recentCommissions: []
    }
  },
  computed: {
    ...mapState({
      distributorInfo: state => state.distributor.info
    })
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        // 获取分销链接统计
        const linkStatsRes = await this.$http.get('/api/promotions/links/stats/')
        this.linkStats = linkStatsRes.data

        // 获取团队统计
        const teamStatsRes = await this.$http.get('/api/promotions/teams/stats/')
        this.teamStats = teamStatsRes.data

        // 获取最近佣金记录
        const commissionsRes = await this.$http.get('/api/promotions/commissions/')
        this.recentCommissions = commissionsRes.data.results.slice(0, 5)
      } catch (error) {
        this.$message.error('获取数据失败')
      }
    },
    getStatusType(status) {
      const types = {
        pending: 'warning',
        frozen: 'info',
        available: 'success',
        withdrawn: 'success',
        cancelled: 'danger'
      }
      return types[status] || 'info'
    },
    getStatusText(status) {
      const texts = {
        pending: '待结算',
        frozen: '已冻结',
        available: '可提现',
        withdrawn: '已提现',
        cancelled: '已取消'
      }
      return texts[status] || status
    }
  }
}
</script>

<style lang="scss" scoped>
.distributor-dashboard {
  .mt-20 {
    margin-top: 20px;
  }

  .data-item {
    text-align: center;
    padding: 20px 0;

    .data-title {
      font-size: 14px;
      color: #909399;
      margin-bottom: 10px;
    }

    .data-value {
      font-size: 24px;
      color: #303133;
      font-weight: bold;
    }
  }

  .stat-item {
    text-align: center;
    padding: 20px 0;

    .stat-title {
      font-size: 14px;
      color: #909399;
      margin-bottom: 10px;
    }

    .stat-value {
      font-size: 20px;
      color: #303133;
      font-weight: bold;
    }
  }
}
</style> 