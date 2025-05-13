<template>
  <div class="distributor-links">
    <!-- 分销链接列表 -->
    <el-card>
      <div slot="header">
        <span>分销链接列表</span>
        <el-button
          style="float: right"
          type="primary"
          size="small"
          @click="showCreateDialog"
        >
          创建新链接
        </el-button>
      </div>
      <el-table :data="links" style="width: 100%">
        <el-table-column prop="name" label="链接名称" width="180" />
        <el-table-column prop="url" label="链接地址" min-width="300">
          <template slot-scope="scope">
            <el-input
              v-model="scope.row.url"
              readonly
              class="copy-input"
            >
              <el-button
                slot="append"
                icon="el-icon-copy-document"
                @click="copyLink(scope.row.url)"
              />
            </el-input>
          </template>
        </el-table-column>
        <el-table-column prop="clicks" label="点击次数" width="120" />
        <el-table-column prop="orders" label="订单数" width="120" />
        <el-table-column prop="commission" label="佣金" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.commission }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button
              type="text"
              size="small"
              @click="showEditDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="text"
              size="small"
              class="delete-btn"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑链接对话框 -->
    <el-dialog
      :title="dialogType === 'create' ? '创建分销链接' : '编辑分销链接'"
      :visible.sync="dialogVisible"
      width="500px"
    >
      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="链接名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入链接名称" />
        </el-form-item>
        <el-form-item label="目标商品" prop="product">
          <el-select
            v-model="form.product"
            filterable
            remote
            placeholder="请输入商品名称搜索"
            :remote-method="searchProducts"
            :loading="loading"
          >
            <el-option
              v-for="item in products"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
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
export default {
  name: 'DistributorLinks',
  data() {
    return {
      links: [],
      dialogVisible: false,
      dialogType: 'create', // create or edit
      form: {
        name: '',
        product: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入链接名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        product: [
          { required: true, message: '请选择目标商品', trigger: 'change' }
        ]
      },
      products: [],
      loading: false
    }
  },
  created() {
    this.fetchLinks()
  },
  methods: {
    async fetchLinks() {
      try {
        const res = await this.$http.get('/api/promotions/links/')
        this.links = res.data.results
      } catch (error) {
        this.$message.error('获取分销链接失败')
      }
    },
    showCreateDialog() {
      this.dialogType = 'create'
      this.form = {
        name: '',
        product: ''
      }
      this.dialogVisible = true
    },
    showEditDialog(link) {
      this.dialogType = 'edit'
      this.form = {
        id: link.id,
        name: link.name,
        product: link.product_id
      }
      this.dialogVisible = true
    },
    async searchProducts(query) {
      if (query) {
        this.loading = true
        try {
          const res = await this.$http.get('/api/products/search/', {
            params: { q: query }
          })
          this.products = res.data.results
        } catch (error) {
          this.$message.error('搜索商品失败')
        }
        this.loading = false
      } else {
        this.products = []
      }
    },
    async handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            if (this.dialogType === 'create') {
              await this.$http.post('/api/promotions/links/', this.form)
              this.$message.success('创建成功')
            } else {
              await this.$http.put(`/api/promotions/links/${this.form.id}/`, this.form)
              this.$message.success('更新成功')
            }
            this.dialogVisible = false
            this.fetchLinks()
          } catch (error) {
            this.$message.error(error.response?.data?.message || '操作失败')
          }
        }
      })
    },
    async handleDelete(link) {
      try {
        await this.$confirm('确认删除该分销链接吗？', '提示', {
          type: 'warning'
        })
        await this.$http.delete(`/api/promotions/links/${link.id}/`)
        this.$message.success('删除成功')
        this.fetchLinks()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    },
    copyLink(url) {
      navigator.clipboard.writeText(url).then(() => {
        this.$message.success('链接已复制到剪贴板')
      }).catch(() => {
        this.$message.error('复制失败，请手动复制')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.distributor-links {
  .copy-input {
    .el-input__inner {
      background-color: #f5f7fa;
    }
  }

  .delete-btn {
    color: #f56c6c;
  }
}
</style> 