<template>
  <div class="distributor-team">
    <!-- 团队概览 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">团队总人数</div>
            <div class="data-value">{{ teamStats.total_members }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">一级分销商</div>
            <div class="data-value">{{ teamStats.level1_members }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">二级分销商</div>
            <div class="data-value">{{ teamStats.level2_members }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 团队成员列表 -->
    <el-card class="mt-20">
      <div slot="header">
        <span>团队成员</span>
        <el-radio-group v-model="levelFilter" size="small" style="float: right">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="1">一级分销商</el-radio-button>
          <el-radio-button label="2">二级分销商</el-radio-button>
        </el-radio-group>
      </div>
      <el-table
        :data="members"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="level" label="分销层级" width="100">
          <template slot-scope="scope">
            {{ scope.row.level === 1 ? '一级' : '二级' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_sales" label="总销售额" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.total_sales }}
          </template>
        </el-table-column>
        <el-table-column prop="total_commission" label="总佣金" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.total_commission }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="加入时间" />
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button
              type="text"
              size="small"
              @click="showMemberDetail(scope.row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        />
      </div>
    </el-card>

    <!-- 成员详情对话框 -->
    <el-dialog
      title="成员详情"
      :visible.sync="detailDialogVisible"
      width="800px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ currentMember.username }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ currentMember.real_name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentMember.phone }}</el-descriptions-item>
        <el-descriptions-item label="分销层级">
          {{ currentMember.level === 1 ? '一级' : '二级' }}
        </el-descriptions-item>
        <el-descriptions-item label="总销售额">¥{{ currentMember.total_sales }}</el-descriptions-item>
        <el-descriptions-item label="总佣金">¥{{ currentMember.total_commission }}</el-descriptions-item>
        <el-descriptions-item label="加入时间">{{ currentMember.created_at }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentMember.is_active ? 'success' : 'danger'">
            {{ currentMember.is_active ? '正常' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 销售记录 -->
      <div class="mt-20">
        <h3>销售记录</h3>
        <el-table :data="currentMember.sales_records" style="width: 100%">
          <el-table-column prop="order_number" label="订单号" width="180" />
          <el-table-column prop="amount" label="订单金额" width="120">
            <template slot-scope="scope">
              ¥{{ scope.row.amount }}
            </template>
          </el-table-column>
          <el-table-column prop="commission" label="佣金" width="120">
            <template slot-scope="scope">
              ¥{{ scope.row.commission }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'DistributorTeam',
  data() {
    return {
      loading: false,
      levelFilter: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      members: [],
      teamStats: {
        total_members: 0,
        level1_members: 0,
        level2_members: 0
      },
      detailDialogVisible: false,
      currentMember: {
        username: '',
        real_name: '',
        phone: '',
        level: 1,
        total_sales: 0,
        total_commission: 0,
        created_at: '',
        is_active: true,
        sales_records: []
      }
    }
  },
  watch: {
    levelFilter() {
      this.currentPage = 1
      this.fetchMembers()
    }
  },
  created() {
    this.fetchTeamStats()
    this.fetchMembers()
  },
  methods: {
    async fetchTeamStats() {
      try {
        const res = await this.$http.get('/api/promotions/teams/stats/')
        this.teamStats = res.data
      } catch (error) {
        this.$message.error('获取团队统计失败')
      }
    },
    async fetchMembers() {
      this.loading = true
      try {
        const res = await this.$http.get('/api/promotions/teams/', {
          params: {
            page: this.currentPage,
            page_size: this.pageSize,
            level: this.levelFilter
          }
        })
        this.members = res.data.results
        this.total = res.data.count
      } catch (error) {
        this.$message.error('获取团队成员失败')
      }
      this.loading = false
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchMembers()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchMembers()
    },
    async showMemberDetail(member) {
      try {
        const res = await this.$http.get(`/api/promotions/teams/${member.id}/`)
        this.currentMember = res.data
        this.detailDialogVisible = true
      } catch (error) {
        this.$message.error('获取成员详情失败')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.distributor-team {
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

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
}
</style> 