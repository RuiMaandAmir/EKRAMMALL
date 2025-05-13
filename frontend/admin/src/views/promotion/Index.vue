<template>
  <div class="promotion-container">
    <el-tabs v-model="activeTab">
      <!-- 优惠券管理 -->
      <el-tab-pane label="优惠券管理" name="coupon">
        <div class="operation-bar">
          <el-button type="primary" @click="handleAddCoupon">新增优惠券</el-button>
        </div>
        <el-table :data="coupons" style="width: 100%">
          <el-table-column prop="name" label="优惠券名称" />
          <el-table-column prop="code" label="优惠码" />
          <el-table-column prop="discount_type" label="优惠类型">
            <template slot-scope="scope">
              {{ scope.row.discount_type === 'fixed' ? '固定金额' : '百分比' }}
            </template>
          </el-table-column>
          <el-table-column prop="discount_value" label="优惠值" />
          <el-table-column prop="min_purchase" label="最低消费" />
          <el-table-column prop="used_count" label="已使用/总量">
            <template slot-scope="scope">
              {{ scope.row.used_count }}/{{ scope.row.quantity }}
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态">
            <template slot-scope="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'info'">
                {{ scope.row.is_active ? '有效' : '无效' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button size="mini" @click="handleEditCoupon(scope.row)">编辑</el-button>
              <el-button size="mini" type="danger" @click="handleDeleteCoupon(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 促销活动管理 -->
      <el-tab-pane label="促销活动管理" name="activity">
        <div class="operation-bar">
          <el-button type="primary" @click="handleAddActivity">新增活动</el-button>
        </div>
        <el-table :data="activities" style="width: 100%">
          <el-table-column prop="name" label="活动名称" />
          <el-table-column prop="start_date" label="开始时间" />
          <el-table-column prop="end_date" label="结束时间" />
          <el-table-column prop="is_active" label="状态">
            <template slot-scope="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'info'">
                {{ scope.row.is_active ? '进行中' : '已结束' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button size="mini" @click="handleEditActivity(scope.row)">编辑</el-button>
              <el-button size="mini" @click="handleManageProducts(scope.row)">管理商品</el-button>
              <el-button size="mini" type="danger" @click="handleDeleteActivity(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 优惠券表单对话框 -->
    <el-dialog :title="couponDialog.title" :visible.sync="couponDialog.visible">
      <el-form :model="couponForm" :rules="couponRules" ref="couponForm" label-width="100px">
        <el-form-item label="优惠券名称" prop="name">
          <el-input v-model="couponForm.name" />
        </el-form-item>
        <el-form-item label="优惠码" prop="code">
          <el-input v-model="couponForm.code" />
        </el-form-item>
        <el-form-item label="优惠类型" prop="discount_type">
          <el-select v-model="couponForm.discount_type">
            <el-option label="固定金额" value="fixed" />
            <el-option label="百分比" value="percentage" />
          </el-select>
        </el-form-item>
        <el-form-item label="优惠值" prop="discount_value">
          <el-input-number v-model="couponForm.discount_value" :min="0" />
        </el-form-item>
        <el-form-item label="最低消费" prop="min_purchase">
          <el-input-number v-model="couponForm.min_purchase" :min="0" />
        </el-form-item>
        <el-form-item label="发放数量" prop="quantity">
          <el-input-number v-model="couponForm.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="有效期" prop="dateRange">
          <el-date-picker
            v-model="couponForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="couponForm.is_active" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="couponDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitCoupon">确定</el-button>
      </div>
    </el-dialog>

    <!-- 促销活动表单对话框 -->
    <el-dialog :title="activityDialog.title" :visible.sync="activityDialog.visible">
      <el-form :model="activityForm" :rules="activityRules" ref="activityForm" label-width="100px">
        <el-form-item label="活动名称" prop="name">
          <el-input v-model="activityForm.name" />
        </el-form-item>
        <el-form-item label="活动描述" prop="description">
          <el-input type="textarea" v-model="activityForm.description" />
        </el-form-item>
        <el-form-item label="活动时间" prop="dateRange">
          <el-date-picker
            v-model="activityForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="activityForm.is_active" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="activityDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitActivity">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getCoupons, createCoupon, updateCoupon, deleteCoupon } from '@/api/coupon'
import { getActivities, createActivity, updateActivity, deleteActivity } from '@/api/activity'

export default {
  name: 'PromotionManagement',
  data() {
    return {
      activeTab: 'coupon',
      coupons: [],
      activities: [],
      couponDialog: {
        visible: false,
        title: '新增优惠券'
      },
      activityDialog: {
        visible: false,
        title: '新增活动'
      },
      couponForm: {
        name: '',
        code: '',
        discount_type: 'fixed',
        discount_value: 0,
        min_purchase: 0,
        quantity: 1,
        dateRange: [],
        is_active: true
      },
      activityForm: {
        name: '',
        description: '',
        dateRange: [],
        is_active: true
      },
      couponRules: {
        name: [{ required: true, message: '请输入优惠券名称', trigger: 'blur' }],
        code: [{ required: true, message: '请输入优惠码', trigger: 'blur' }],
        discount_type: [{ required: true, message: '请选择优惠类型', trigger: 'change' }],
        discount_value: [{ required: true, message: '请输入优惠值', trigger: 'blur' }],
        quantity: [{ required: true, message: '请输入发放数量', trigger: 'blur' }],
        dateRange: [{ required: true, message: '请选择有效期', trigger: 'change' }]
      },
      activityRules: {
        name: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
        description: [{ required: true, message: '请输入活动描述', trigger: 'blur' }],
        dateRange: [{ required: true, message: '请选择活动时间', trigger: 'change' }]
      }
    }
  },
  created() {
    this.fetchCoupons()
    this.fetchActivities()
  },
  methods: {
    async fetchCoupons() {
      try {
        const { data } = await getCoupons()
        this.coupons = data
      } catch (error) {
        this.$message.error('获取优惠券列表失败')
      }
    },
    async fetchActivities() {
      try {
        const { data } = await getActivities()
        this.activities = data
      } catch (error) {
        this.$message.error('获取活动列表失败')
      }
    },
    handleAddCoupon() {
      this.couponDialog.title = '新增优惠券'
      this.couponForm = {
        name: '',
        code: '',
        discount_type: 'fixed',
        discount_value: 0,
        min_purchase: 0,
        quantity: 1,
        dateRange: [],
        is_active: true
      }
      this.couponDialog.visible = true
    },
    handleEditCoupon(row) {
      this.couponDialog.title = '编辑优惠券'
      this.couponForm = { ...row }
      this.couponForm.dateRange = [row.start_date, row.end_date]
      this.couponDialog.visible = true
    },
    async handleSubmitCoupon() {
      try {
        this.$refs.couponForm.validate(async valid => {
          if (valid) {
            const formData = {
              ...this.couponForm,
              start_date: this.couponForm.dateRange[0],
              end_date: this.couponForm.dateRange[1]
            }
            delete formData.dateRange
            
            if (this.couponDialog.title === '新增优惠券') {
              await createCoupon(formData)
              this.$message.success('创建优惠券成功')
            } else {
              await updateCoupon(formData)
              this.$message.success('更新优惠券成功')
            }
            this.couponDialog.visible = false
            this.fetchCoupons()
          }
        })
      } catch (error) {
        this.$message.error('操作失败')
      }
    },
    async handleDeleteCoupon(row) {
      try {
        await this.$confirm('确认删除该优惠券吗？', '提示', {
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
    handleAddActivity() {
      this.activityDialog.title = '新增活动'
      this.activityForm = {
        name: '',
        description: '',
        dateRange: [],
        is_active: true
      }
      this.activityDialog.visible = true
    },
    handleEditActivity(row) {
      this.activityDialog.title = '编辑活动'
      this.activityForm = { ...row }
      this.activityForm.dateRange = [row.start_date, row.end_date]
      this.activityDialog.visible = true
    },
    async handleSubmitActivity() {
      try {
        this.$refs.activityForm.validate(async valid => {
          if (valid) {
            const formData = {
              ...this.activityForm,
              start_date: this.activityForm.dateRange[0],
              end_date: this.activityForm.dateRange[1]
            }
            delete formData.dateRange
            
            if (this.activityDialog.title === '新增活动') {
              await createActivity(formData)
              this.$message.success('创建活动成功')
            } else {
              await updateActivity(formData)
              this.$message.success('更新活动成功')
            }
            this.activityDialog.visible = false
            this.fetchActivities()
          }
        })
      } catch (error) {
        this.$message.error('操作失败')
      }
    },
    async handleDeleteActivity(row) {
      try {
        await this.$confirm('确认删除该活动吗？', '提示', {
          type: 'warning'
        })
        await deleteActivity(row.id)
        this.$message.success('删除成功')
        this.fetchActivities()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    },
    handleManageProducts(row) {
      this.$router.push({
        name: 'PromotionProducts',
        params: { activityId: row.id }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.promotion-container {
  padding: 20px;
  
  .operation-bar {
    margin-bottom: 20px;
  }
}
</style> 