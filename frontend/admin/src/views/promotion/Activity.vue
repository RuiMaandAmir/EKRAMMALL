<template>
  <div class="activity-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>促销活动管理</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="showCreateDialog">创建活动</el-button>
      </div>
      
      <!-- 搜索和筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="活动名称">
          <el-input v-model="searchForm.name" placeholder="请输入活动名称"></el-input>
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

      <!-- 活动列表 -->
      <el-table :data="activityList" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="活动名称" width="180"></el-table-column>
        <el-table-column prop="description" label="活动描述" width="300"></el-table-column>
        <el-table-column prop="start_date" label="开始时间" width="180"></el-table-column>
        <el-table-column prop="end_date" label="结束时间" width="180"></el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="mini" type="primary" @click="handleManageProducts(scope.row)">管理商品</el-button>
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

    <!-- 创建/编辑活动对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="50%">
      <el-form :model="activityForm" :rules="rules" ref="activityForm" label-width="100px">
        <el-form-item label="活动名称" prop="name">
          <el-input v-model="activityForm.name"></el-input>
        </el-form-item>
        <el-form-item label="活动描述" prop="description">
          <el-input type="textarea" v-model="activityForm.description"></el-input>
        </el-form-item>
        <el-form-item label="有效期" prop="dateRange">
          <el-date-picker
            v-model="activityForm.dateRange"
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

    <!-- 管理商品对话框 -->
    <el-dialog title="管理活动商品" :visible.sync="productDialogVisible" width="70%">
      <div class="product-management">
        <div class="product-header">
          <el-button type="primary" @click="showAddProductDialog">添加商品</el-button>
        </div>
        
        <el-table :data="productList" style="width: 100%" v-loading="productLoading">
          <el-table-column prop="product.name" label="商品名称" width="180"></el-table-column>
          <el-table-column prop="product.price" label="原价" width="120">
            <template slot-scope="scope">
              ¥{{ scope.row.product.price }}
            </template>
          </el-table-column>
          <el-table-column prop="promotion_price" label="促销价" width="120">
            <template slot-scope="scope">
              ¥{{ scope.row.promotion_price }}
            </template>
          </el-table-column>
          <el-table-column prop="stock" label="库存" width="120"></el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button size="mini" @click="handleEditProduct(scope.row)">编辑</el-button>
              <el-button size="mini" type="danger" @click="handleRemoveProduct(scope.row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加/编辑商品对话框 -->
    <el-dialog :title="productDialogTitle" :visible.sync="addProductDialogVisible" width="50%">
      <el-form :model="productForm" :rules="productRules" ref="productForm" label-width="100px">
        <el-form-item label="选择商品" prop="product_id">
          <el-select v-model="productForm.product_id" placeholder="请选择商品" filterable>
            <el-option
              v-for="item in availableProducts"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="促销价" prop="promotion_price">
          <el-input-number v-model="productForm.promotion_price" :min="0" :precision="2" :step="1"></el-input-number>
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="productForm.stock" :min="0" :step="1"></el-input-number>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addProductDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleProductSubmit">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { 
  getActivities, createActivity, updateActivity, deleteActivity,
  getActivityProducts, addActivityProduct, updateActivityProduct, removeActivityProduct,
  getAvailableProducts
} from '@/api/promotion'

export default {
  name: 'Activity',
  data() {
    return {
      searchForm: {
        name: '',
        status: ''
      },
      activityList: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogTitle: '创建活动',
      activityForm: {
        name: '',
        description: '',
        dateRange: []
      },
      rules: {
        name: [
          { required: true, message: '请输入活动名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入活动描述', trigger: 'blur' }
        ],
        dateRange: [
          { required: true, message: '请选择有效期', trigger: 'change' }
        ]
      },
      productDialogVisible: false,
      productList: [],
      productLoading: false,
      currentActivityId: null,
      addProductDialogVisible: false,
      productDialogTitle: '添加商品',
      productForm: {
        product_id: '',
        promotion_price: 0,
        stock: 0
      },
      productRules: {
        product_id: [
          { required: true, message: '请选择商品', trigger: 'change' }
        ],
        promotion_price: [
          { required: true, message: '请输入促销价', trigger: 'blur' }
        ],
        stock: [
          { required: true, message: '请输入库存', trigger: 'blur' }
        ]
      },
      availableProducts: []
    }
  },
  created() {
    this.fetchActivities()
  },
  methods: {
    async fetchActivities() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.searchForm
        }
        const res = await getActivities(params)
        this.activityList = res.data.results
        this.total = res.data.count
      } catch (error) {
        this.$message.error('获取活动列表失败')
      } finally {
        this.loading = false
      }
    },
    async fetchActivityProducts(activityId) {
      this.productLoading = true
      try {
        const res = await getActivityProducts(activityId)
        this.productList = res.data
      } catch (error) {
        this.$message.error('获取活动商品失败')
      } finally {
        this.productLoading = false
      }
    },
    async fetchAvailableProducts() {
      try {
        const res = await getAvailableProducts()
        this.availableProducts = res.data
      } catch (error) {
        this.$message.error('获取可选商品失败')
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.fetchActivities()
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
      this.fetchActivities()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchActivities()
    },
    showCreateDialog() {
      this.dialogTitle = '创建活动'
      this.activityForm = {
        name: '',
        description: '',
        dateRange: []
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑活动'
      this.activityForm = {
        id: row.id,
        name: row.name,
        description: row.description,
        dateRange: [row.start_date, row.end_date]
      }
      this.dialogVisible = true
    },
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该活动吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
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
    async handleSubmit() {
      try {
        await this.$refs.activityForm.validate()
        const formData = {
          ...this.activityForm,
          start_date: this.activityForm.dateRange[0],
          end_date: this.activityForm.dateRange[1]
        }
        delete formData.dateRange
        
        if (this.activityForm.id) {
          await updateActivity(this.activityForm.id, formData)
          this.$message.success('更新成功')
        } else {
          await createActivity(formData)
          this.$message.success('创建成功')
        }
        this.dialogVisible = false
        this.fetchActivities()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('操作失败')
        }
      }
    },
    async handleManageProducts(row) {
      this.currentActivityId = row.id
      this.productDialogVisible = true
      await this.fetchActivityProducts(row.id)
      await this.fetchAvailableProducts()
    },
    showAddProductDialog() {
      this.productDialogTitle = '添加商品'
      this.productForm = {
        product_id: '',
        promotion_price: 0,
        stock: 0
      }
      this.addProductDialogVisible = true
    },
    handleEditProduct(row) {
      this.productDialogTitle = '编辑商品'
      this.productForm = {
        id: row.id,
        product_id: row.product.id,
        promotion_price: row.promotion_price,
        stock: row.stock
      }
      this.addProductDialogVisible = true
    },
    async handleRemoveProduct(row) {
      try {
        await this.$confirm('确认从活动中移除该商品吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await removeActivityProduct(this.currentActivityId, row.id)
        this.$message.success('移除成功')
        this.fetchActivityProducts(this.currentActivityId)
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('移除失败')
        }
      }
    },
    async handleProductSubmit() {
      try {
        await this.$refs.productForm.validate()
        if (this.productForm.id) {
          await updateActivityProduct(this.currentActivityId, this.productForm.id, this.productForm)
          this.$message.success('更新成功')
        } else {
          await addActivityProduct(this.currentActivityId, this.productForm)
          this.$message.success('添加成功')
        }
        this.addProductDialogVisible = false
        this.fetchActivityProducts(this.currentActivityId)
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
.activity-container {
  padding: 20px;
}
.search-form {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
.product-management {
  padding: 20px;
}
.product-header {
  margin-bottom: 20px;
}
</style> 