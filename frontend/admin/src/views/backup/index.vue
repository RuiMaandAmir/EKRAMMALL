<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>数据库备份管理</span>
          <el-button type="primary" @click="handleBackup" :loading="backupLoading">
            <el-icon><Download /></el-icon>
            立即备份
          </el-button>
        </div>
      </template>
      
      <el-alert
        title="重要提示: 数据库操作涉及系统核心数据，请谨慎操作！建议定期备份数据，以防数据丢失。"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-table
        v-loading="listLoading"
        :data="backupList"
        border
        style="width: 100%"
      >
        <el-table-column prop="filename" label="备份文件名" min-width="250" />
        
        <el-table-column label="备份大小" width="120" align="center">
          <template #default="scope">
            {{ formatFileSize(scope.row.size) }}
          </template>
        </el-table-column>
        
        <el-table-column label="备份时间" width="180" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" align="center">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="handleDownload(scope.row)"
            >
              下载
            </el-button>
            
            <el-button
              size="small"
              type="success"
              @click="handleRestore(scope.row)"
              :loading="scope.row.restoreLoading"
            >
              恢复
            </el-button>
            
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(scope.row)"
              :loading="scope.row.deleteLoading"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>导入数据库</span>
        </div>
      </template>
      
      <el-alert
        title="您可以导入之前下载的数据库备份文件，导入过程将覆盖当前系统数据，请确保备份文件的正确性。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-upload
        class="upload-demo"
        drag
        action="/api/settings/upload-backup"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :limit="1"
        accept=".sql,.gz,.zip"
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">拖拽备份文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">
            请上传SQL或压缩格式的备份文件，大小不超过100MB
          </div>
        </template>
      </el-upload>
    </el-card>
    
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>系统缓存管理</span>
        </div>
      </template>
      
      <el-alert
        title="清除系统缓存可以释放服务器资源，解决某些功能异常。但可能会暂时影响系统性能，建议在访问量较少时操作。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <div class="cache-actions">
        <el-button
          type="primary"
          @click="handleClearCache('all')"
          :loading="cacheLoading === 'all'"
        >
          清除全部缓存
        </el-button>
        
        <el-button
          type="info"
          @click="handleClearCache('data')"
          :loading="cacheLoading === 'data'"
        >
          清除数据缓存
        </el-button>
        
        <el-button
          type="info"
          @click="handleClearCache('template')"
          :loading="cacheLoading === 'template'"
        >
          清除模板缓存
        </el-button>
        
        <el-button
          type="info"
          @click="handleClearCache('config')"
          :loading="cacheLoading === 'config'"
        >
          清除配置缓存
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Download, Upload } from '@element-plus/icons-vue';
import { 
  getBackupList, 
  backupDatabase, 
  restoreDatabase, 
  deleteBackup,
  clearCache
} from '@/api/settings';

// 状态控制
const listLoading = ref(false);
const backupLoading = ref(false);
const cacheLoading = ref('');

// 备份列表
const backupList = ref([]);

// 获取备份列表
const fetchBackupList = async () => {
  listLoading.value = true;
  try {
    const res = await getBackupList();
    backupList.value = res.data.map(item => ({
      ...item,
      restoreLoading: false,
      deleteLoading: false
    }));
  } catch (error) {
    console.error('获取备份列表失败:', error);
    ElMessage.error('获取备份列表失败');
  } finally {
    listLoading.value = false;
  }
};

// 创建备份
const handleBackup = async () => {
  backupLoading.value = true;
  try {
    await backupDatabase();
    ElMessage.success('数据库备份成功');
    fetchBackupList(); // 刷新列表
  } catch (error) {
    console.error('数据库备份失败:', error);
    ElMessage.error('数据库备份失败: ' + (error.message || '未知错误'));
  } finally {
    backupLoading.value = false;
  }
};

// 下载备份
const handleDownload = (row) => {
  // 创建下载链接
  const link = document.createElement('a');
  link.href = `/api/settings/download-backup?filename=${encodeURIComponent(row.filename)}`;
  link.setAttribute('download', row.filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 恢复备份
const handleRestore = (row) => {
  ElMessageBox.confirm(
    '恢复操作将覆盖当前系统的所有数据，且无法撤销。确定要恢复此备份吗？',
    '警告',
    {
      confirmButtonText: '确定恢复',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    }
  ).then(async () => {
    row.restoreLoading = true;
    try {
      await restoreDatabase(row.filename);
      ElMessage.success('数据库恢复成功');
    } catch (error) {
      console.error('数据库恢复失败:', error);
      ElMessage.error('数据库恢复失败: ' + (error.message || '未知错误'));
    } finally {
      row.restoreLoading = false;
    }
  }).catch(() => {
    // 取消操作
  });
};

// 删除备份
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '删除操作将永久移除此备份文件，且无法恢复。确定要删除吗？',
    '警告',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    row.deleteLoading = true;
    try {
      await deleteBackup(row.filename);
      ElMessage.success('备份文件删除成功');
      // 从列表中移除
      const index = backupList.value.findIndex(item => item.filename === row.filename);
      if (index !== -1) {
        backupList.value.splice(index, 1);
      }
    } catch (error) {
      console.error('删除备份文件失败:', error);
      ElMessage.error('删除备份文件失败: ' + (error.message || '未知错误'));
    } finally {
      row.deleteLoading = false;
    }
  }).catch(() => {
    // 取消操作
  });
};

// 清除缓存
const handleClearCache = async (type) => {
  cacheLoading.value = type;
  try {
    await clearCache(type);
    ElMessage.success('缓存清除成功');
  } catch (error) {
    console.error('清除缓存失败:', error);
    ElMessage.error('清除缓存失败: ' + (error.message || '未知错误'));
  } finally {
    cacheLoading.value = '';
  }
};

// 上传备份文件前的检查
const beforeUpload = (file) => {
  const isValidType = 
    file.type === 'application/sql' || 
    file.type === 'application/x-sql' || 
    file.type === 'application/gzip' || 
    file.type === 'application/zip' ||
    file.name.endsWith('.sql') ||
    file.name.endsWith('.gz') ||
    file.name.endsWith('.zip');
    
  const isLt100M = file.size / 1024 / 1024 < 100;

  if (!isValidType) {
    ElMessage.error('请上传SQL或压缩格式的备份文件!');
    return false;
  }
  
  if (!isLt100M) {
    ElMessage.error('备份文件大小不能超过100MB!');
    return false;
  }
  
  return true;
};

// 上传成功处理
const handleUploadSuccess = (response, file) => {
  ElMessage.success('备份文件上传成功');
  
  // 询问是否立即恢复
  ElMessageBox.confirm(
    '备份文件上传成功，是否立即恢复数据？',
    '提示',
    {
      confirmButtonText: '立即恢复',
      cancelButtonText: '稍后处理',
      type: 'info'
    }
  ).then(async () => {
    try {
      await restoreDatabase(response.data.filename);
      ElMessage.success('数据库恢复成功');
      fetchBackupList(); // 刷新列表
    } catch (error) {
      console.error('数据库恢复失败:', error);
      ElMessage.error('数据库恢复失败: ' + (error.message || '未知错误'));
    }
  }).catch(() => {
    fetchBackupList(); // 刷新列表
  });
};

// 上传失败处理
const handleUploadError = (error) => {
  console.error('上传备份文件失败:', error);
  ElMessage.error('上传备份文件失败: ' + (error.message || '未知错误'));
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 初始化
onMounted(() => {
  fetchBackupList();
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
  
  .box-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .cache-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
  }
  
  .el-upload {
    width: 100%;
    
    .el-upload-dragger {
      width: 100%;
    }
  }
}
</style> 