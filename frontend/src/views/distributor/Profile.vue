<template>
  <div class="distributor-profile">
    <el-row :gutter="20">
      <!-- 基本信息 -->
      <el-col :span="16">
        <el-card>
          <div slot="header">
            <span>基本信息</span>
            <el-button
              style="float: right"
              type="primary"
              size="small"
              @click="handleEdit"
            >
              编辑
            </el-button>
          </div>
          <el-form
            ref="form"
            :model="form"
            :rules="rules"
            label-width="100px"
            :disabled="!isEditing"
          >
            <el-form-item label="用户名">
              <el-input v-model="form.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="真实姓名" prop="real_name">
              <el-input v-model="form.real_name" />
            </el-form-item>
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="form.id_card" />
            </el-form-item>
            <el-form-item label="银行名称" prop="bank_name">
              <el-input v-model="form.bank_name" />
            </el-form-item>
            <el-form-item label="开户支行" prop="bank_branch">
              <el-input v-model="form.bank_branch" />
            </el-form-item>
            <el-form-item label="银行账号" prop="bank_account">
              <el-input v-model="form.bank_account" />
            </el-form-item>
            <el-form-item v-if="isEditing">
              <el-button type="primary" @click="handleSave">保存</el-button>
              <el-button @click="cancelEdit">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 认证信息 -->
      <el-col :span="8">
        <el-card>
          <div slot="header">
            <span>认证信息</span>
          </div>
          <div class="auth-info">
            <div class="auth-item">
              <div class="auth-label">认证状态</div>
              <el-tag :type="getAuthStatusType(distributorInfo.is_verified)">
                {{ getAuthStatusText(distributorInfo.is_verified) }}
              </el-tag>
            </div>
            <div class="auth-item">
              <div class="auth-label">账户状态</div>
              <el-tag :type="getAccountStatusType(distributorInfo.is_active)">
                {{ getAccountStatusText(distributorInfo.is_active) }}
              </el-tag>
            </div>
            <div class="auth-item">
              <div class="auth-label">注册时间</div>
              <div class="auth-value">{{ distributorInfo.created_at }}</div>
            </div>
          </div>

          <!-- 身份证照片 -->
          <div class="id-card-photos" v-if="distributorInfo.is_verified">
            <div class="photo-item">
              <div class="photo-label">身份证正面</div>
              <el-image
                :src="distributorInfo.id_card_front"
                :preview-src-list="[distributorInfo.id_card_front]"
                fit="cover"
              />
            </div>
            <div class="photo-item">
              <div class="photo-label">身份证反面</div>
              <el-image
                :src="distributorInfo.id_card_back"
                :preview-src-list="[distributorInfo.id_card_back]"
                fit="cover"
              />
            </div>
          </div>

          <!-- 未认证时显示上传按钮 -->
          <div v-else class="upload-section">
            <el-upload
              class="upload-demo"
              action="/api/promotions/authenticate/"
              :headers="uploadHeaders"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
            >
              <el-button type="primary">上传身份证照片</el-button>
              <div class="upload-tip">
                请上传清晰的身份证正反面照片
              </div>
            </el-upload>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'DistributorProfile',
  data() {
    return {
      isEditing: false,
      form: {
        username: '',
        email: '',
        phone: '',
        real_name: '',
        id_card: '',
        bank_name: '',
        bank_branch: '',
        bank_account: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ],
        real_name: [
          { required: true, message: '请输入真实姓名', trigger: 'blur' }
        ],
        id_card: [
          { required: true, message: '请输入身份证号', trigger: 'blur' },
          { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
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
    }),
    uploadHeaders() {
      return {
        Authorization: `Bearer ${this.$store.state.user.token}`
      }
    }
  },
  created() {
    this.initForm()
  },
  methods: {
    initForm() {
      this.form = {
        username: this.distributorInfo.username,
        email: this.distributorInfo.email,
        phone: this.distributorInfo.phone,
        real_name: this.distributorInfo.real_name,
        id_card: this.distributorInfo.id_card,
        bank_name: this.distributorInfo.bank_name,
        bank_branch: this.distributorInfo.bank_branch,
        bank_account: this.distributorInfo.bank_account
      }
    },
    handleEdit() {
      this.isEditing = true
    },
    cancelEdit() {
      this.isEditing = false
      this.initForm()
    },
    async handleSave() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            await this.$http.put('/api/promotions/profile/', this.form)
            this.$message.success('保存成功')
            this.isEditing = false
            await this.$store.dispatch('distributor/getInfo')
          } catch (error) {
            this.$message.error(error.response?.data?.message || '保存失败')
          }
        }
      })
    },
    getAuthStatusType(isVerified) {
      return isVerified ? 'success' : 'warning'
    },
    getAuthStatusText(isVerified) {
      return isVerified ? '已认证' : '未认证'
    },
    getAccountStatusType(isActive) {
      return isActive ? 'success' : 'danger'
    },
    getAccountStatusText(isActive) {
      return isActive ? '正常' : '已禁用'
    },
    beforeUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isImage) {
        this.$message.error('只能上传图片文件！')
        return false
      }
      if (!isLt2M) {
        this.$message.error('图片大小不能超过 2MB！')
        return false
      }
      return true
    },
    handleUploadSuccess(response) {
      this.$message.success('上传成功')
      this.$store.dispatch('distributor/getInfo')
    },
    handleUploadError() {
      this.$message.error('上传失败')
    }
  }
}
</script>

<style lang="scss" scoped>
.distributor-profile {
  .auth-info {
    .auth-item {
      margin-bottom: 20px;

      .auth-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }

      .auth-value {
        font-size: 14px;
        color: #303133;
      }
    }
  }

  .id-card-photos {
    margin-top: 20px;

    .photo-item {
      margin-bottom: 20px;

      .photo-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }

      .el-image {
        width: 100%;
        height: 200px;
        border-radius: 4px;
      }
    }
  }

  .upload-section {
    margin-top: 20px;

    .upload-tip {
      font-size: 12px;
      color: #909399;
      margin-top: 8px;
    }
  }
}
</style> 