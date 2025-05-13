<template>
    <div class="coupon-container">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>优惠券管理</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="showCreateDialog">创建优惠券</el-button>
        </div>
        
        <!-- 搜索和筛选 -->
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="优惠券名称">
            <el-input v-model="searchForm.name" placeholder="请输入优惠券名称"></el-input>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态">
              <el-option label="全部" value=""></el-option>
              <el-option label="未开始" value="pending"></el-option>
              <el-option label="进行中" value="active"></el-option>
              <el-option label="已结束" value="ended"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
  
        <!-- 优惠券列表 -->
        <el-table :data="couponList" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="优惠券名称" width="180"></el-table-column>
          <el-table-column prop="discount_type" label="优惠类型" width="120">
            <template slot-scope="scope">
              {{ scope.row.discount_type === 'fixed' ? '固定金额' : '百分比' }}
            </template>
          </el-table-column>
          <el-table-column prop="discount_value" label="优惠值" width="120">
            <template slot-scope="scope">
              {{ scope.row.discount_type === 'fixed' ? `¥${scope.row.discount_value}` : `${scope.row.discount_value}%` }}
            </template>
          </el-table-column>
          <el-table-column prop="min_purchase" label="最低消费" width="120">
            <template slot-scope="scope">
              ¥{{ scope.row.min_purchase }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="发行数量" width="120"></el-table-column>
          <el-table-column prop="used_count" label="已使用" width="120"></el-table-column>
          <el-table-column prop="start_date" label="开始时间" width="180"></el-table-column>
          <el-table-column prop="end_date" label="结束时间" width="180"></el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template slot-scope="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
  
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </el-card>
  
      <!-- 创建/编辑优惠券对话框 -->
      <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="50%">
        <el-form :model="couponForm" :rules="rules" ref="couponForm" label-width="100px">
          <el-form-item label="优惠券名称" prop="name">
            <el-input v-model="couponForm.name"></el-input>
          </el-form-item>
          <el-form-item label="优惠类型" prop="discount_type">
            <el-radio-group v-model="couponForm.discount_type">
              <el-radio label="fixed">固定金额</el-radio>
              <el-radio label="percentage">百分比</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="优惠值" prop="discount_value">
            <el-input-number 
              v-model="couponForm.discount_value" 
              :min="0" 
              :precision="couponForm.discount_type === 'fixed' ? 2 : 0"
              :step="couponForm.discount_type === 'fixed' ? 1 : 1">
            </el-input-number>
          </el-form-item>
          <el-form-item label="最低消费" prop="min_purchase">
            <el-input-number v-model="couponForm.min_purchase" :min="0" :precision="2" :step="1"></el-input-number>
          </el-form-item>
          <el-form-item label="发行数量" prop="quantity">
            <el-input-number v-model="couponForm.quantity" :min="1" :step="1"></el-input-number>
          </el-form-item>
          <el-form-item label="有效期" prop="dateRange">
            <el-date-picker
              v-model="couponForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="yyyy-MM-dd">
            </el-date-picker>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </div>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import { getCoupons, createCoupon, updateCoupon, deleteCoupon } from '@/api/promotion'
  
  export default {
    name: 'Coupon',
    data() {
      return {
        searchForm: {
          name: '',
          status: ''
        },
        couponList: [],
        loading: false,
        currentPage: 1,
        pageSize: 10,
        total: 0,
        dialogVisible: false,
        dialogTitle: '创建优惠券',
        couponForm: {
          name: '',
          discount_type: 'fixed',
          discount_value: 0,
          min_purchase: 0,
          quantity: 1,
          dateRange: []
        },
        rules: {
          name: [
            { required: true, message: '请输入优惠券名称', trigger: 'blur' },
            { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
          ],
          discount_type: [
            { required: true, message: '请选择优惠类型', trigger: 'change' }
          ],
          discount_value: [
            { required: true, message: '请输入优惠值', trigger: 'blur' }
          ],
          min_purchase: [
            { required: true, message: '请输入最低消费', trigger: 'blur' }
          ],
          quantity: [
            { required: true, message: '请输入发行数量', trigger: 'blur' }
          ],
          dateRange: [
            { required: true, message: '请选择有效期', trigger: 'change' }
          ]
        }
      }
    },
    created() {
      this.fetchCoupons()
    },
    methods: {
      async fetchCoupons() {
        this.loading = true
        try {
          const params = {
            page: this.currentPage,
            page_size: this.pageSize,
            ...this.searchForm
          }
          const res = await getCoupons(params)
          this.couponList = res.data.results
          this.total = res.data.count
        } catch (error) {
          this.$message.error('获取优惠券列表失败')
        } finally {
          this.loading = false
        }
      },
      handleSearch() {
        this.currentPage = 1
        this.fetchCoupons()
      },
      resetSearch() {
        this.searchForm = {
          name: '',
          status: ''
        }
        this.handleSearch()
      },
      handleSizeChange(val) {
        this.pageSize = val
        this.fetchCoupons()
      },
      handleCurrentChange(val) {
        this.currentPage = val
        this.fetchCoupons()
      },
      showCreateDialog() {
        this.dialogTitle = '创建优惠券'
        this.couponForm = {
          name: '',
          discount_type: 'fixed',
          discount_value: 0,
          min_purchase: 0,
          quantity: 1,
          dateRange: []
        }
        this.dialogVisible = true
      },
      handleEdit(row) {
        this.dialogTitle = '编辑优惠券'
        this.couponForm = {
          id: row.id,
          name: row.name,
          discount_type: row.discount_type,
          discount_value: row.discount_value,
          min_purchase: row.min_purchase,
          quantity: row.quantity,
          dateRange: [row.start_date, row.end_date]
        }
        this.dialogVisible = true
      },
      async handleDelete(row) {
        try {
          await this.$confirm('确认删除该优惠券吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          })
          await deleteCoupon(row.id)
          this.$message.success('删除成功')
          this.fetchCoupons()
        } catch (error) {
          if (error !== 'cancel') {
            this.$message.error('删除失败')
          }
        }
      },
      async handleSubmit() {
        try {
          await this.$refs.couponForm.validate()
          const formData = {
            ...this.couponForm,
            start_date: this.couponForm.dateRange[0],
            end_date: this.couponForm.dateRange[1]
          }
          delete formData.dateRange
          
          if (this.couponForm.id) {
            await updateCoupon(this.couponForm.id, formData)
            this.$message.success('更新成功')
          } else {
            await createCoupon(formData)
            this.$message.success('创建成功')
          }
          this.dialogVisible = false
          this.fetchCoupons()
        } catch (error) {
          if (error !== 'cancel') {
            this.$message.error('操作失败')
          }
        }
      },
      getStatusType(status) {
        const types = {
          pending: 'info',
          active: 'success',
          ended: 'danger'
        }
        return types[status] || 'info'
      },
      getStatusText(status) {
        const texts = {
          pending: '未开始',
          active: '进行中',
          ended: '已结束'
        }
        return texts[status] || '未知'
      }
    }
  }
  </script>
  
  <style scoped>
  .coupon-container {
    padding: 20px;
  }
  .search-form {
    margin-bottom: 20px;
  }
  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
  </style>