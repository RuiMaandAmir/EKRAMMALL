<template>
  <div class="promotion-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑促销活动' : '创建促销活动' }}</span>
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
        <el-form-item label="活动名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入活动名称" maxlength="50" show-word-limit />
        </el-form-item>
        
        <el-form-item label="活动类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择活动类型" style="width: 100%;">
            <el-option label="打折" value="discount" />
            <el-option label="固定价格" value="fixed_price" />
            <el-option label="满减" value="cash_off" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="form.type === 'discount'" label="折扣率" prop="discount">
          <el-input-number 
            v-model="form.discount" 
            :min="0.1" 
            :max="1" 
            :step="0.1" 
            :precision="2"
            style="width: 100%;"
            placeholder="请输入折扣率（0.1-1之间，如0.8表示8折）"
          />
        </el-form-item>
        
        <el-form-item v-if="form.type === 'fixed_price'" label="固定价格" prop="fixed_price">
          <el-input-number 
            v-model="form.fixed_price" 
            :min="0" 
            :step="1" 
            style="width: 100%;"
            placeholder="请输入固定价格（元）"
          />
        </el-form-item>
        
        <el-form-item v-if="form.type === 'cash_off'" label="满减门槛" prop="threshold">
          <el-input-number 
            v-model="form.threshold" 
            :min="0" 
            :step="1" 
            style="width: 100%;" 
            placeholder="请输入满减门槛（元）"
          />
        </el-form-item>
        
        <el-form-item v-if="form.type === 'cash_off'" label="减免金额" prop="cash_off">
          <el-input-number 
            v-model="form.cash_off" 
            :min="0" 
            :step="1" 
            style="width: 100%;" 
            placeholder="请输入减免金额（元）"
          />
        </el-form-item>
        
        <el-form-item label="活动时间" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="活动说明" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入活动说明"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="是否启用" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">{{ isEdit ? '保存修改' : '创建活动' }}</el-button>
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
import { getActivities, createActivity, updateActivity } from '@/api/promotion';

const router = useRouter();
const route = useRoute();
const loading = ref(false);
const formRef = ref(null);

// 判断是编辑还是创建
const isEdit = computed(() => {
  return route.params.id !== undefined;
});

// 表单数据
const form = reactive({
  name: '',
  type: 'discount',
  discount: 0.8,
  fixed_price: 0,
  threshold: 0,
  cash_off: 0,
  dateRange: [],
  description: '',
  is_active: true
});

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入活动名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择活动类型', trigger: 'change' }
  ],
  discount: [
    { required: true, message: '请输入折扣率', trigger: 'blur' }
  ],
  fixed_price: [
    { required: true, message: '请输入固定价格', trigger: 'blur' }
  ],
  threshold: [
    { required: true, message: '请输入满减门槛', trigger: 'blur' }
  ],
  cash_off: [
    { required: true, message: '请输入减免金额', trigger: 'blur' }
  ],
  dateRange: [
    { required: true, message: '请选择活动时间', trigger: 'change' }
  ],
  description: [
    { max: 200, message: '最多输入200个字符', trigger: 'blur' }
  ]
};

// 获取活动详情
const getActivityDetail = async (id) => {
  loading.value = true;
  try {
    const response = await getActivities({ id });
    const activityData = response.data.items[0] || response.data;
    
    // 填充表单数据
    form.name = activityData.name;
    form.type = activityData.type;
    form.discount = activityData.discount || 0.8;
    form.fixed_price = activityData.fixed_price || 0;
    form.threshold = activityData.threshold || 0;
    form.cash_off = activityData.cash_off || 0;
    form.description = activityData.description || '';
    form.is_active = activityData.is_active !== undefined ? activityData.is_active : true;
    
    // 设置日期范围
    if (activityData.start_time && activityData.end_time) {
      form.dateRange = [activityData.start_time, activityData.end_time];
    }
  } catch (error) {
    console.error('获取活动详情失败:', error);
    ElMessage.error('获取活动详情失败');
  } finally {
    loading.value = false;
  }
};

// 提交表单
const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      
      try {
        // 构建提交数据
        const data = {
          name: form.name,
          type: form.type,
          description: form.description,
          is_active: form.is_active,
          start_time: form.dateRange[0],
          end_time: form.dateRange[1]
        };
        
        // 根据活动类型添加不同的字段
        if (form.type === 'discount') {
          data.discount = form.discount;
        } else if (form.type === 'fixed_price') {
          data.fixed_price = form.fixed_price;
        } else if (form.type === 'cash_off') {
          data.threshold = form.threshold;
          data.cash_off = form.cash_off;
        }
        
        if (isEdit.value) {
          // 编辑模式
          await updateActivity(route.params.id, data);
          ElMessage.success('活动更新成功');
        } else {
          // 创建模式
          await createActivity(data);
          ElMessage.success('活动创建成功');
        }
        
        // 返回列表页
        router.push('/promotion/list');
      } catch (error) {
        console.error('保存活动失败:', error);
        ElMessage.error('保存活动失败');
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
  router.push('/promotion/list');
};

onMounted(() => {
  if (isEdit.value) {
    getActivityDetail(route.params.id);
  }
});
</script>

<style lang="scss" scoped>
.promotion-detail {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style> 