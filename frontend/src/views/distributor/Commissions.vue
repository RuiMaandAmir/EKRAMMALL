<template>
  <div class="distributor-commissions">
    <!-- 佣金概览 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">可提现佣金</div>
            <div class="data-value">¥{{ distributorInfo.available_commission }}</div>
            <el-button
              type="primary"
              size="small"
              :disabled="distributorInfo.available_commission < 100"
              @click="showWithdrawDialog"
            >
              申请提现
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">已冻结佣金</div>
            <div class="data-value">¥{{ distributorInfo.frozen_commission }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">总佣金</div>
            <div class="data-value">¥{{ distributorInfo.total_commission }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 佣金记录 -->
    <el-card class="mt-20">
      <div slot="header">
        <span>佣金记录</span>
        <el-radio-group v-model="statusFilter" size="small" style="float: right">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="pending">待结算</el-radio-button>
          <el-radio-button label="frozen">已冻结</el-radio-button>
          <el-radio-button label="available">可提现</el-radio-button>
          <el-radio-button label="withdrawn">已提现</el-radio-button>
        </el-radio-group>
      </div>
      <el-table
        :data="commissions"
        style="width: 100%"
        v-loading="loading"
      >
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

    <!-- 提现对话框 -->
    <el-dialog
      title="申请提现"
      :visible.sync="withdrawDialogVisible"
      width="500px"
    >
      <el-form
        ref="withdrawForm"
        :model="withdrawForm"
        :rules="withdrawRules"
        label-width="100px"
      >
        <el-form-item label="提现金额" prop="amount">
          <el-input-number
            v-model="withdrawForm.amount"
            :min="100"
            :max="distributorInfo.available_commission"
            :step="100"
          />
          <div class="form-tip">
            最低提现金额：¥100
          </div>
        </el-form-item>
        <el-form-item label="银行名称" prop="bank_name">
          <el-input v-model="withdrawForm.bank_name" />
        </el-form-item>
        <el-form-item label="开户支行" prop="bank_branch">
          <el-input v-model="withdrawForm.bank_branch" />
        </el-form-item>
        <el-form-item label="银行账号" prop="bank_account">
          <el-input v-model="withdrawForm.bank_account" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="withdrawDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleWithdraw">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'DistributorCommissions',
  data() {
    return {
      loading: false,
      statusFilter: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      commissions: [],
      withdrawDialogVisible: false,
      withdrawForm: {
        amount: 100,
        bank_name: '',
        bank_branch: '',
        bank_account: ''
      },
      withdrawRules: {
        amount: [
          { required: true, message: '请输入提现金额', trigger: 'blur' },
          { type: 'number', min: 100, message: '最低提现金额为100元', trigger: 'blur' }
        ],
        bank_name: [
          { required: true, message: '请输入银行名称', trigger: 'blur' }
        ],
        bank_branch: [
          { required: true, message: '请输入开户支行', trigger: 'blur' }
        ],
        bank_account: [
          { required: true, message: '请输入银行账号', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapState({
      distributorInfo: state => state.distributor.info
    })
  },
  watch: {
    statusFilter() {
      this.currentPage = 1
      this.fetchCommissions()
    }
  },
  created() {
    this.fetchCommissions()
  },
  methods: {
    async fetchCommissions() {
      this.loading = true
      try {
        const res = await this.$http.get('/api/promotions/commissions/', {
          params: {
            page: this.currentPage,
            page_size: this.pageSize,
            status: this.statusFilter
          }
        })
        this.commissions = res.data.results
        this.total = res.data.count
      } catch (error) {
        this.$message.error('获取佣金记录失败')
      }
      this.loading = false
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchCommissions()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchCommissions()
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
    },
    showWithdrawDialog() {
      this.withdrawForm = {
        amount: 100,
        bank_name: this.distributorInfo.bank_name || '',
        bank_branch: this.distributorInfo.bank_branch || '',
        bank_account: this.distributorInfo.bank_account || ''
      }
      this.withdrawDialogVisible = true
    },
    async handleWithdraw() {
      this.$refs.withdrawForm.validate(async valid => {
        if (valid) {
          try {
            await this.$http.post('/api/promotions/withdrawals/', this.withdrawForm)
            this.$message.success('提现申请已提交')
            this.withdrawDialogVisible = false
            this.fetchCommissions()
          } catch (error) {
            this.$message.error(error.response?.data?.message || '提现申请失败')
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.distributor-commissions {
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
      margin-bottom: 15px;
    }
  }

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}
</style> 