<template>
  <div class="product-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑商品' : '新增商品' }}</span>
          <el-button @click="goBack">返回列表</el-button>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" maxlength="100" show-word-limit />
        </el-form-item>
        
        <el-form-item label="商品分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择商品分类" style="width: 100%;">
            <el-option 
              v-for="item in categoryOptions" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="商品价格" prop="price">
          <el-input-number 
            v-model="form.price" 
            :min="0.01" 
            :precision="2"
            :step="1" 
            style="width: 100%;"
            placeholder="请输入商品价格（元）"
          />
        </el-form-item>
        
        <el-form-item label="商品原价" prop="original_price">
          <el-input-number 
            v-model="form.original_price" 
            :min="0" 
            :precision="2"
            :step="1" 
            style="width: 100%;"
            placeholder="请输入商品原价（元）"
          />
        </el-form-item>
        
        <el-form-item label="商品库存" prop="stock">
          <el-input-number 
            v-model="form.stock" 
            :min="0" 
            :step="1" 
            style="width: 100%;" 
            placeholder="请输入商品库存"
          />
        </el-form-item>
        
        <el-form-item label="商品主图" prop="image_url">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/image/"
            :headers="{ Authorization: `Bearer ${getToken()}` }"
            :show-file-list="false"
            :on-success="handleImageSuccess"
            :before-upload="beforeImageUpload"
          >
            <img v-if="form.image_url" :src="form.image_url" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">建议上传尺寸为800×800px的图片</div>
        </el-form-item>
        
        <el-form-item label="商品图集" prop="images">
          <el-upload
            action="/api/upload/image/"
            list-type="picture-card"
            :headers="{ Authorization: `Bearer ${getToken()}` }"
            :on-success="handleImagesSuccess"
            :on-remove="handleImagesRemove"
            :file-list="imageFileList"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商品描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="商品详情" prop="details">
          <!-- 简化版的富文本编辑器 -->
          <el-input
            v-model="form.details"
            type="textarea"
            :rows="8"
            placeholder="请输入商品详情，支持HTML格式"
          />
        </el-form-item>
        
        <el-form-item label="是否上架" prop="status">
          <el-switch
            v-model="form.status"
            active-value="active"
            inactive-value="inactive"
            active-text="上架"
            inactive-text="下架"
          />
        </el-form-item>
        
        <el-form-item label="排序权重" prop="sort_order">
          <el-input-number 
            v-model="form.sort_order" 
            :min="0" 
            :step="1" 
            style="width: 100%;" 
            placeholder="数值越大越靠前展示"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">{{ isEdit ? '保存修改' : '创建商品' }}</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { getProduct, createProduct, updateProduct, getCategories } from '@/api/product';
import { getToken } from '@/utils/auth';

const router = useRouter();
const route = useRoute();
const loading = ref(false);
const formRef = ref(null);
const categoryOptions = ref([]);
const imageFileList = ref([]);

// 判断是编辑还是创建
const isEdit = computed(() => {
  return route.params.id !== undefined;
});

// 表单数据
const form = reactive({
  name: '',
  category_id: '',
  price: 0,
  original_price: 0,
  stock: 0,
  image_url: '',
  images: [],
  description: '',
  details: '',
  status: 'inactive',
  sort_order: 0
});

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入商品库存', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存不能小于0', trigger: 'blur' }
  ],
  image_url: [
    { required: true, message: '请上传商品主图', trigger: 'change' }
  ],
  description: [
    { max: 500, message: '描述最多500个字符', trigger: 'blur' }
  ]
};

// 获取商品详情
const getProductDetail = async (id) => {
  loading.value = true;
  try {
    const response = await getProduct(id);
    const productData = response.data;
    
    // 填充表单数据
    Object.keys(form).forEach(key => {
      if (productData[key] !== undefined) {
        form[key] = productData[key];
      }
    });
    
    // 处理图片列表
    if (productData.images && productData.images.length > 0) {
      imageFileList.value = productData.images.map((url, index) => ({
        name: `image-${index}`,
        url
      }));
    }
  } catch (error) {
    console.error('获取商品详情失败:', error);
    ElMessage.error('获取商品详情失败');
  } finally {
    loading.value = false;
  }
};

// 获取商品分类
const fetchCategories = async () => {
  try {
    const response = await getCategories();
    categoryOptions.value = response.data || [];
  } catch (error) {
    console.error('获取商品分类失败:', error);
    ElMessage.error('获取商品分类失败');
  }
};

// 图片上传前的处理
const beforeImageUpload = (file) => {
  const isJPG = file.type === 'image/jpeg';
  const isPNG = file.type === 'image/png';
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isJPG && !isPNG) {
    ElMessage.error('上传图片只能是 JPG 或 PNG 格式!');
    return false;
  }
  if (!isLt2M) {
    ElMessage.error('上传图片大小不能超过 2MB!');
    return false;
  }
  return true;
};

// 主图上传成功的处理
const handleImageSuccess = (response, file) => {
  if (response.code === 200) {
    form.image_url = response.data.url;
  } else {
    ElMessage.error('上传失败');
  }
};

// 图集上传成功的处理
const handleImagesSuccess = (response, file, fileList) => {
  if (response.code === 200) {
    form.images.push(response.data.url);
  } else {
    ElMessage.error('上传失败');
  }
};

// 图集移除图片的处理
const handleImagesRemove = (file, fileList) => {
  const index = form.images.indexOf(file.url);
  if (index > -1) {
    form.images.splice(index, 1);
  }
};

// 提交表单
const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      
      try {
        if (isEdit.value) {
          // 编辑模式
          await updateProduct(route.params.id, form);
          ElMessage.success('商品更新成功');
        } else {
          // 创建模式
          await createProduct(form);
          ElMessage.success('商品创建成功');
        }
        
        // 返回列表页
        router.push('/product/list');
      } catch (error) {
        console.error('保存商品失败:', error);
        ElMessage.error('保存商品失败');
      } finally {
        loading.value = false;
      }
    }
  });
};

// 重置表单
const resetForm = () => {
  formRef.value.resetFields();
};

// 返回列表
const goBack = () => {
  router.push('/product/list');
};

onMounted(() => {
  fetchCategories();
  
  if (isEdit.value) {
    getProductDetail(route.params.id);
  }
});
</script>

<style lang="scss" scoped>
.product-detail {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .avatar-uploader {
    width: 178px;
    height: 178px;
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    &:hover {
      border-color: #409EFF;
    }
    
    .avatar {
      width: 178px;
      height: 178px;
      display: block;
    }
    
    .avatar-uploader-icon {
      font-size: 28px;
      color: #8c939d;
      width: 178px;
      height: 178px;
      line-height: 178px;
      text-align: center;
    }
  }
  
  .upload-tip {
    font-size: 12px;
    color: #606266;
    margin-top: 7px;
  }
}
</style> 