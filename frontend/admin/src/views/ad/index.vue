<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="query.title" placeholder="广告标题" style="width: 200px; margin-right: 10px;" />
      <el-button type="primary" icon="el-icon-search" @click="fetchAds">搜索</el-button>
      <el-button type="primary" icon="el-icon-plus" @click="handleCreate">添加广告</el-button>
    </div>
    <el-table :data="adList" border style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column label="图片" width="120" align="center">
        <template #default="scope">
          <el-image :src="scope.row.image" style="width: 80px; height: 40px; object-fit:cover;" v-if="scope.row.image" />
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" width="180" />
      <el-table-column prop="content" label="内容" />
      <el-table-column prop="link" label="跳转链接" width="200" />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status ? 'success' : 'info'">{{ scope.row.status ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="180" align="center">
        <template #default="scope">
          <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.limit"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="fetchAds"
      @current-change="fetchAds"
      style="margin-top: 20px; text-align: right;"
    />
    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '添加广告' : '编辑广告'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入广告标题" />
        </el-form-item>
        <el-form-item label="图片" prop="image">
          <el-input v-model="form.image" placeholder="图片URL，或集成上传组件" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="3" placeholder="请输入广告内容" />
        </el-form-item>
        <el-form-item label="跳转链接" prop="link">
          <el-input v-model="form.link" placeholder="请输入跳转链接（可选）" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="form.status" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getAdList, createAd, updateAd, deleteAd } from '@/api/ad';

const adList = ref([]);
const total = ref(0);
const loading = ref(false);
const query = reactive({ page: 1, limit: 10, title: '' });

const dialogVisible = ref(false);
const dialogType = ref('create');
const formRef = ref(null);
const form = reactive({
  id: undefined,
  title: '',
  image: '',
  content: '',
  link: '',
  status: true
});
const rules = {
  title: [{ required: true, message: '请输入广告标题', trigger: 'blur' }],
  image: [{ required: false }],
  content: [{ required: true, message: '请输入广告内容', trigger: 'blur' }]
};

const fetchAds = async () => {
  loading.value = true;
  try {
    const res = await getAdList(query);
    adList.value = res.data.items || res.data;
    total.value = res.data.total || res.data.length || 0;
  } catch (e) {
    ElMessage.error('获取广告列表失败');
  } finally {
    loading.value = false;
  }
};

const handleCreate = () => {
  dialogType.value = 'create';
  Object.assign(form, { id: undefined, title: '', image: '', content: '', link: '', status: true });
  dialogVisible.value = true;
};

const handleEdit = (row) => {
  dialogType.value = 'edit';
  Object.assign(form, row);
  dialogVisible.value = true;
};

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该广告吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteAd(row.id);
      ElMessage.success('删除成功');
      fetchAds();
    } catch (e) {
      ElMessage.error('删除失败');
    }
  });
};

const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return;
    try {
      if (dialogType.value === 'create') {
        await createAd(form);
        ElMessage.success('创建成功');
      } else {
        await updateAd(form.id, form);
        ElMessage.success('更新成功');
      }
      dialogVisible.value = false;
      fetchAds();
    } catch (e) {
      ElMessage.error('提交失败');
    }
  });
};

onMounted(() => {
  fetchAds();
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}
.filter-container {
  margin-bottom: 20px;
}
</style> 