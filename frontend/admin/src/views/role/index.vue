<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.keyword"
        placeholder="角色名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        搜索
      </el-button>
      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        添加角色
      </el-button>
      <el-button
        :loading="downloadLoading"
        class="filter-item"
        type="success"
        icon="el-icon-download"
        @click="handleDownload"
      >
        导出
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column
        align="center"
        label="ID"
        width="80"
      >
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      
      <el-table-column
        align="center"
        label="角色名称"
        width="180"
      >
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      
      <el-table-column
        align="center"
        label="角色编码"
        width="180"
      >
        <template slot-scope="scope">
          <span>{{ scope.row.code }}</span>
        </template>
      </el-table-column>
      
      <el-table-column
        align="center"
        label="描述"
      >
        <template slot-scope="scope">
          <span>{{ scope.row.description }}</span>
        </template>
      </el-table-column>
      
      <el-table-column
        align="center"
        label="创建时间"
        width="180"
      >
        <template slot-scope="scope">
          <span>{{ scope.row.createdAt | parseTime }}</span>
        </template>
      </el-table-column>
      
      <el-table-column
        align="center"
        label="状态"
        width="120"
      >
        <template slot-scope="scope">
          <el-tag :type="scope.row.status ? 'success' : 'danger'">
            {{ scope.row.status ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column
        align="center"
        label="操作"
        width="260"
      >
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="primary"
            @click="handleUpdate(scope.row)"
          >
            编辑
          </el-button>
          <el-button
            size="mini"
            type="success"
            @click="handlePermission(scope.row)"
          >
            权限配置
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 添加/编辑角色对话框 -->
    <el-dialog
      :title="dialogStatus === 'create' ? '添加角色' : '编辑角色'"
      :visible.sync="dialogFormVisible"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="temp.code" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="temp.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="temp.status"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog
      title="权限配置"
      :visible.sync="permissionDialogVisible"
      width="600px"
    >
      <el-tree
        ref="permissionTree"
        :data="permissionTreeData"
        :props="defaultProps"
        show-checkbox
        node-key="id"
        default-expand-all
      />
      <div slot="footer" class="dialog-footer">
        <el-button @click="permissionDialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="savePermissions">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { 
  getRoleList, 
  createRole, 
  updateRole, 
  deleteRole, 
  getRolePermissions, 
  updateRolePermissions, 
  exportRoles 
} from '@/api/role'
import { getPermissionTree } from '@/api/permission'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'

export default {
  name: 'RoleManagement',
  components: { Pagination },
  filters: {
    parseTime
  },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      downloadLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: ''
      },
      temp: {
        id: undefined,
        name: '',
        code: '',
        description: '',
        status: true
      },
      dialogFormVisible: false,
      dialogStatus: '',
      permissionDialogVisible: false,
      permissionTreeData: [],
      currentRole: {},
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      rules: {
        name: [{ required: true, message: '角色名称不能为空', trigger: 'blur' }],
        code: [{ required: true, message: '角色编码不能为空', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getRoleList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
        code: '',
        description: '',
        status: true
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createRole(this.temp).then(() => {
            this.list.unshift(this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建角色成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // 复制对象，避免影响原数据
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateRole(tempData.id, tempData).then(() => {
            const index = this.list.findIndex(v => v.id === this.temp.id)
            this.list.splice(index, 1, this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新角色成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该角色吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteRole(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除角色成功',
            type: 'success',
            duration: 2000
          })
          this.getList()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handlePermission(row) {
      this.currentRole = row
      this.permissionDialogVisible = true
      
      // 获取权限树数据
      getPermissionTree().then(response => {
        this.permissionTreeData = response.data
        
        // 获取当前角色的权限
        getRolePermissions(row.id).then(res => {
          const permissionIds = res.data.map(item => item.id)
          this.$nextTick(() => {
            this.$refs.permissionTree.setCheckedKeys(permissionIds)
          })
        })
      })
    },
    savePermissions() {
      const checkedKeys = this.$refs.permissionTree.getCheckedKeys()
      const halfCheckedKeys = this.$refs.permissionTree.getHalfCheckedKeys()
      const permissionIds = [...checkedKeys, ...halfCheckedKeys]
      
      updateRolePermissions(this.currentRole.id, permissionIds).then(() => {
        this.permissionDialogVisible = false
        this.$notify({
          title: '成功',
          message: '权限配置成功',
          type: 'success',
          duration: 2000
        })
      })
    },
    handleDownload() {
      this.downloadLoading = true
      exportRoles().then(response => {
        // 处理下载逻辑
        const blob = new Blob([response], { type: 'application/vnd.ms-excel' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = '角色列表.xlsx'
        link.click()
        URL.revokeObjectURL(link.href)
        this.downloadLoading = false
      }).catch(() => {
        this.downloadLoading = false
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    display: inline-block;
    vertical-align: middle;
    margin-bottom: 10px;
    margin-right: 10px;
  }
}
</style> 