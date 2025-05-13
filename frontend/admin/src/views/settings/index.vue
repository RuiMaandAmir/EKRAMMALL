<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础设置" name="basic">
          <el-form 
            ref="basicFormRef" 
            :model="basicForm" 
            :rules="basicRules" 
            label-width="120px"
            class="setting-form"
          >
            <el-form-item label="网站名称" prop="siteName">
              <el-input v-model="basicForm.siteName" placeholder="请输入网站名称" />
            </el-form-item>
            
            <el-form-item label="网站Logo">
              <el-upload
                class="avatar-uploader"
                action="/api/uploads"
                :show-file-list="false"
                :on-success="handleLogoSuccess"
                :before-upload="beforeLogoUpload"
              >
                <img v-if="basicForm.logo" :src="basicForm.logo" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">建议尺寸: 200 x 60 像素, 支持 jpg、png 格式，大小不超过 2MB</div>
            </el-form-item>
            
            <el-form-item label="网站图标">
              <el-upload
                class="avatar-uploader"
                action="/api/uploads"
                :show-file-list="false"
                :on-success="handleFaviconSuccess"
                :before-upload="beforeFaviconUpload"
              >
                <img v-if="basicForm.favicon" :src="basicForm.favicon" class="avatar favicon" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">建议尺寸: 32 x 32 像素, 支持 ico、png 格式，大小不超过 1MB</div>
            </el-form-item>
            
            <el-form-item label="联系电话" prop="contactPhone">
              <el-input v-model="basicForm.contactPhone" placeholder="请输入联系电话" />
            </el-form-item>
            
            <el-form-item label="联系邮箱" prop="contactEmail">
              <el-input v-model="basicForm.contactEmail" placeholder="请输入联系邮箱" />
            </el-form-item>
            
            <el-form-item label="ICP备案号" prop="icp">
              <el-input v-model="basicForm.icp" placeholder="请输入ICP备案号" />
            </el-form-item>
            
            <el-form-item label="公安备案号" prop="psr">
              <el-input v-model="basicForm.psr" placeholder="请输入公安备案号" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitBasicForm">保存设置</el-button>
              <el-button @click="resetBasicForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="支付设置" name="payment">
          <el-form 
            ref="paymentFormRef" 
            :model="paymentForm"
            label-width="120px"
            class="setting-form"
          >
            <el-divider content-position="left">支付宝设置</el-divider>
            
            <el-form-item label="是否启用">
              <el-switch v-model="paymentForm.alipayEnabled" />
            </el-form-item>
            
            <el-form-item label="应用ID" v-if="paymentForm.alipayEnabled">
              <el-input v-model="paymentForm.alipayAppId" placeholder="请输入支付宝应用ID" />
            </el-form-item>
            
            <el-form-item label="商户私钥" v-if="paymentForm.alipayEnabled">
              <el-input 
                v-model="paymentForm.alipayPrivateKey" 
                type="textarea" 
                :rows="4"
                placeholder="请输入商户私钥" 
              />
            </el-form-item>
            
            <el-form-item label="支付宝公钥" v-if="paymentForm.alipayEnabled">
              <el-input 
                v-model="paymentForm.alipayPublicKey" 
                type="textarea" 
                :rows="4"
                placeholder="请输入支付宝公钥" 
              />
            </el-form-item>
            
            <el-divider content-position="left">微信支付设置</el-divider>
            
            <el-form-item label="是否启用">
              <el-switch v-model="paymentForm.wechatEnabled" />
            </el-form-item>
            
            <el-form-item label="商户ID" v-if="paymentForm.wechatEnabled">
              <el-input v-model="paymentForm.wechatMchId" placeholder="请输入微信商户ID" />
            </el-form-item>
            
            <el-form-item label="应用ID" v-if="paymentForm.wechatEnabled">
              <el-input v-model="paymentForm.wechatAppId" placeholder="请输入微信应用ID" />
            </el-form-item>
            
            <el-form-item label="API密钥" v-if="paymentForm.wechatEnabled">
              <el-input v-model="paymentForm.wechatApiKey" placeholder="请输入微信API密钥" show-password />
            </el-form-item>
            
            <el-form-item label="API证书" v-if="paymentForm.wechatEnabled">
              <el-upload
                class="cert-uploader"
                action="/api/uploads/cert"
                :show-file-list="true"
                :file-list="wechatCertFiles"
                :limit="1"
                :on-success="handleWechatCertSuccess"
                :on-remove="handleWechatCertRemove"
              >
                <el-button type="primary">上传证书</el-button>
                <template #tip>
                  <div class="upload-tip">请上传apiclient_cert.p12文件</div>
                </template>
              </el-upload>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitPaymentForm">保存设置</el-button>
              <el-button @click="resetPaymentForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="物流设置" name="shipping">
          <el-form 
            ref="shippingFormRef" 
            :model="shippingForm"
            label-width="120px"
            class="setting-form"
          >
            <el-form-item label="默认物流公司">
              <el-select v-model="shippingForm.defaultCompany" placeholder="请选择默认物流公司">
                <el-option 
                  v-for="item in shippingCompanies"
                  :key="item.code"
                  :label="item.name"
                  :value="item.code"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="物流API接口">
              <el-radio-group v-model="shippingForm.apiType">
                <el-radio label="kuaidi100">快递100</el-radio>
                <el-radio label="aliyun">阿里云物流</el-radio>
                <el-radio label="kdniao">快递鸟</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <template v-if="shippingForm.apiType === 'kuaidi100'">
              <el-form-item label="快递100 Key">
                <el-input v-model="shippingForm.kuaidi100Key" placeholder="请输入快递100 Key" />
              </el-form-item>
              <el-form-item label="快递100 Customer">
                <el-input v-model="shippingForm.kuaidi100Customer" placeholder="请输入快递100 Customer" />
              </el-form-item>
            </template>
            
            <template v-if="shippingForm.apiType === 'aliyun'">
              <el-form-item label="阿里云 AppCode">
                <el-input v-model="shippingForm.aliyunAppCode" placeholder="请输入阿里云 AppCode" />
              </el-form-item>
            </template>
            
            <template v-if="shippingForm.apiType === 'kdniao'">
              <el-form-item label="快递鸟商户ID">
                <el-input v-model="shippingForm.kdniaoBusinessId" placeholder="请输入快递鸟商户ID" />
              </el-form-item>
              <el-form-item label="快递鸟API Key">
                <el-input v-model="shippingForm.kdniaoApiKey" placeholder="请输入快递鸟API Key" />
              </el-form-item>
            </template>
            
            <el-divider content-position="left">运费设置</el-divider>
            
            <el-form-item label="配送方式">
              <el-checkbox-group v-model="shippingForm.methods">
                <el-checkbox label="express">快递配送</el-checkbox>
                <el-checkbox label="pickup">门店自提</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="运费计算方式">
              <el-radio-group v-model="shippingForm.feeType">
                <el-radio label="fixed">统一运费</el-radio>
                <el-radio label="weight">按重量计费</el-radio>
                <el-radio label="amount">按金额计费</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="统一运费" v-if="shippingForm.feeType === 'fixed'">
              <el-input-number v-model="shippingForm.fixedFee" :min="0" :precision="2" />
            </el-form-item>
            
            <template v-if="shippingForm.feeType === 'weight'">
              <el-form-item label="首重(kg)">
                <el-input-number v-model="shippingForm.firstWeight" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="首重费用">
                <el-input-number v-model="shippingForm.firstWeightFee" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="续重(kg)">
                <el-input-number v-model="shippingForm.additionalWeight" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="续重费用">
                <el-input-number v-model="shippingForm.additionalWeightFee" :min="0" :precision="2" />
              </el-form-item>
            </template>
            
            <template v-if="shippingForm.feeType === 'amount'">
              <el-form-item label="免运费订单金额">
                <el-input-number v-model="shippingForm.freeShippingAmount" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="默认运费">
                <el-input-number v-model="shippingForm.defaultFee" :min="0" :precision="2" />
              </el-form-item>
            </template>
            
            <el-form-item>
              <el-button type="primary" @click="submitShippingForm">保存设置</el-button>
              <el-button @click="resetShippingForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="短信设置" name="sms">
          <el-form 
            ref="smsFormRef" 
            :model="smsForm"
            label-width="120px"
            class="setting-form"
          >
            <el-form-item label="短信服务商">
              <el-radio-group v-model="smsForm.provider">
                <el-radio label="aliyun">阿里云</el-radio>
                <el-radio label="tencent">腾讯云</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <template v-if="smsForm.provider === 'aliyun'">
              <el-form-item label="AccessKey ID">
                <el-input v-model="smsForm.aliyunAccessKeyId" placeholder="请输入AccessKey ID" />
              </el-form-item>
              <el-form-item label="AccessKey Secret">
                <el-input v-model="smsForm.aliyunAccessKeySecret" placeholder="请输入AccessKey Secret" show-password />
              </el-form-item>
              <el-form-item label="短信签名">
                <el-input v-model="smsForm.aliyunSignName" placeholder="请输入短信签名" />
              </el-form-item>
            </template>
            
            <template v-if="smsForm.provider === 'tencent'">
              <el-form-item label="SecretId">
                <el-input v-model="smsForm.tencentSecretId" placeholder="请输入SecretId" />
              </el-form-item>
              <el-form-item label="SecretKey">
                <el-input v-model="smsForm.tencentSecretKey" placeholder="请输入SecretKey" show-password />
              </el-form-item>
              <el-form-item label="短信应用SDK AppID">
                <el-input v-model="smsForm.tencentAppId" placeholder="请输入SDK AppID" />
              </el-form-item>
              <el-form-item label="短信签名">
                <el-input v-model="smsForm.tencentSignName" placeholder="请输入短信签名" />
              </el-form-item>
            </template>
            
            <el-divider content-position="left">短信模板</el-divider>
            
            <el-form-item label="验证码模板ID">
              <el-input v-model="smsForm.verifyCodeTemplateId" placeholder="请输入验证码短信模板ID" />
            </el-form-item>
            
            <el-form-item label="订单发货模板ID">
              <el-input v-model="smsForm.orderShippedTemplateId" placeholder="请输入订单发货通知模板ID" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitSmsForm">保存设置</el-button>
              <el-button @click="resetSmsForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { 
  getSystemSettings, 
  updateSystemSettings,
  getShippingCompanies
} from '@/api/settings';

// 当前激活的标签页
const activeTab = ref('basic');

// 表单引用
const basicFormRef = ref(null);
const paymentFormRef = ref(null);
const shippingFormRef = ref(null);
const smsFormRef = ref(null);

// 微信支付证书文件列表
const wechatCertFiles = ref([]);

// 基础设置表单
const basicForm = reactive({
  siteName: '',
  logo: '',
  favicon: '',
  contactPhone: '',
  contactEmail: '',
  icp: '',
  psr: ''
});

// 支付设置表单
const paymentForm = reactive({
  alipayEnabled: false,
  alipayAppId: '',
  alipayPrivateKey: '',
  alipayPublicKey: '',
  wechatEnabled: false,
  wechatMchId: '',
  wechatAppId: '',
  wechatApiKey: '',
  wechatCertPath: ''
});

// 物流设置表单
const shippingForm = reactive({
  defaultCompany: '',
  apiType: 'kuaidi100',
  kuaidi100Key: '',
  kuaidi100Customer: '',
  aliyunAppCode: '',
  kdniaoBusinessId: '',
  kdniaoApiKey: '',
  methods: ['express'],
  feeType: 'fixed',
  fixedFee: 10,
  firstWeight: 1,
  firstWeightFee: 10,
  additionalWeight: 1,
  additionalWeightFee: 5,
  freeShippingAmount: 99,
  defaultFee: 10
});

// 物流公司列表
const shippingCompanies = ref([]);

// 短信设置表单
const smsForm = reactive({
  provider: 'aliyun',
  aliyunAccessKeyId: '',
  aliyunAccessKeySecret: '',
  aliyunSignName: '',
  tencentSecretId: '',
  tencentSecretKey: '',
  tencentAppId: '',
  tencentSignName: '',
  verifyCodeTemplateId: '',
  orderShippedTemplateId: ''
});

// 基础表单验证规则
const basicRules = {
  siteName: [
    { required: true, message: '请输入网站名称', trigger: 'blur' }
  ],
  contactPhone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  contactEmail: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};

// 获取系统设置数据
const fetchSettings = async () => {
  try {
    const res = await getSystemSettings();
    const data = res.data;
    
    // 填充基础设置表单
    basicForm.siteName = data.basic.siteName;
    basicForm.logo = data.basic.logo;
    basicForm.favicon = data.basic.favicon;
    basicForm.contactPhone = data.basic.contactPhone;
    basicForm.contactEmail = data.basic.contactEmail;
    basicForm.icp = data.basic.icp;
    basicForm.psr = data.basic.psr;
    
    // 填充支付设置表单
    paymentForm.alipayEnabled = data.payment.alipayEnabled;
    paymentForm.alipayAppId = data.payment.alipayAppId;
    paymentForm.alipayPrivateKey = data.payment.alipayPrivateKey;
    paymentForm.alipayPublicKey = data.payment.alipayPublicKey;
    paymentForm.wechatEnabled = data.payment.wechatEnabled;
    paymentForm.wechatMchId = data.payment.wechatMchId;
    paymentForm.wechatAppId = data.payment.wechatAppId;
    paymentForm.wechatApiKey = data.payment.wechatApiKey;
    paymentForm.wechatCertPath = data.payment.wechatCertPath;
    
    // 如果有微信支付证书路径，添加到文件列表
    if (data.payment.wechatCertPath) {
      wechatCertFiles.value = [
        {
          name: '微信支付证书',
          url: data.payment.wechatCertPath
        }
      ];
    }
    
    // 填充物流设置表单
    shippingForm.defaultCompany = data.shipping.defaultCompany;
    shippingForm.apiType = data.shipping.apiType;
    shippingForm.kuaidi100Key = data.shipping.kuaidi100Key;
    shippingForm.kuaidi100Customer = data.shipping.kuaidi100Customer;
    shippingForm.aliyunAppCode = data.shipping.aliyunAppCode;
    shippingForm.kdniaoBusinessId = data.shipping.kdniaoBusinessId;
    shippingForm.kdniaoApiKey = data.shipping.kdniaoApiKey;
    shippingForm.methods = data.shipping.methods;
    shippingForm.feeType = data.shipping.feeType;
    shippingForm.fixedFee = data.shipping.fixedFee;
    shippingForm.firstWeight = data.shipping.firstWeight;
    shippingForm.firstWeightFee = data.shipping.firstWeightFee;
    shippingForm.additionalWeight = data.shipping.additionalWeight;
    shippingForm.additionalWeightFee = data.shipping.additionalWeightFee;
    shippingForm.freeShippingAmount = data.shipping.freeShippingAmount;
    shippingForm.defaultFee = data.shipping.defaultFee;
    
    // 填充短信设置表单
    smsForm.provider = data.sms.provider;
    smsForm.aliyunAccessKeyId = data.sms.aliyunAccessKeyId;
    smsForm.aliyunAccessKeySecret = data.sms.aliyunAccessKeySecret;
    smsForm.aliyunSignName = data.sms.aliyunSignName;
    smsForm.tencentSecretId = data.sms.tencentSecretId;
    smsForm.tencentSecretKey = data.sms.tencentSecretKey;
    smsForm.tencentAppId = data.sms.tencentAppId;
    smsForm.tencentSignName = data.sms.tencentSignName;
    smsForm.verifyCodeTemplateId = data.sms.verifyCodeTemplateId;
    smsForm.orderShippedTemplateId = data.sms.orderShippedTemplateId;
    
  } catch (error) {
    console.error('获取系统设置失败:', error);
    ElMessage.error('获取系统设置失败');
  }
};

// 获取物流公司列表
const fetchShippingCompanies = async () => {
  try {
    const res = await getShippingCompanies();
    shippingCompanies.value = res.data;
  } catch (error) {
    console.error('获取物流公司列表失败:', error);
  }
};

// Logo上传相关方法
const handleLogoSuccess = (res, file) => {
  basicForm.logo = res.data.url;
  ElMessage.success('Logo上传成功');
};

const beforeLogoUpload = (file) => {
  const isImage = file.type === 'image/jpeg' || file.type === 'image/png';
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage.error('Logo只能是JPG或PNG格式!');
  }
  if (!isLt2M) {
    ElMessage.error('Logo大小不能超过2MB!');
  }
  return isImage && isLt2M;
};

// Favicon上传相关方法
const handleFaviconSuccess = (res, file) => {
  basicForm.favicon = res.data.url;
  ElMessage.success('网站图标上传成功');
};

const beforeFaviconUpload = (file) => {
  const isValidType = file.type === 'image/png' || file.type === 'image/x-icon';
  const isLt1M = file.size / 1024 / 1024 < 1;

  if (!isValidType) {
    ElMessage.error('网站图标只能是ICO或PNG格式!');
  }
  if (!isLt1M) {
    ElMessage.error('网站图标大小不能超过1MB!');
  }
  return isValidType && isLt1M;
};

// 微信支付证书上传相关方法
const handleWechatCertSuccess = (res, file) => {
  paymentForm.wechatCertPath = res.data.path;
  ElMessage.success('证书上传成功');
};

const handleWechatCertRemove = () => {
  paymentForm.wechatCertPath = '';
};

// 保存基础设置
const submitBasicForm = () => {
  basicFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await updateSystemSettings({
          type: 'basic',
          data: basicForm
        });
        ElMessage.success('基础设置保存成功');
      } catch (error) {
        console.error('保存基础设置失败:', error);
        ElMessage.error('保存基础设置失败');
      }
    } else {
      return false;
    }
  });
};

// 重置基础设置
const resetBasicForm = () => {
  basicFormRef.value.resetFields();
  fetchSettings();
};

// 保存支付设置
const submitPaymentForm = async () => {
  try {
    await updateSystemSettings({
      type: 'payment',
      data: paymentForm
    });
    ElMessage.success('支付设置保存成功');
  } catch (error) {
    console.error('保存支付设置失败:', error);
    ElMessage.error('保存支付设置失败');
  }
};

// 重置支付设置
const resetPaymentForm = () => {
  fetchSettings();
};

// 保存物流设置
const submitShippingForm = async () => {
  try {
    await updateSystemSettings({
      type: 'shipping',
      data: shippingForm
    });
    ElMessage.success('物流设置保存成功');
  } catch (error) {
    console.error('保存物流设置失败:', error);
    ElMessage.error('保存物流设置失败');
  }
};

// 重置物流设置
const resetShippingForm = () => {
  fetchSettings();
};

// 保存短信设置
const submitSmsForm = async () => {
  try {
    await updateSystemSettings({
      type: 'sms',
      data: smsForm
    });
    ElMessage.success('短信设置保存成功');
  } catch (error) {
    console.error('保存短信设置失败:', error);
    ElMessage.error('保存短信设置失败');
  }
};

// 重置短信设置
const resetSmsForm = () => {
  fetchSettings();
};

// 初始化页面数据
onMounted(() => {
  fetchSettings();
  fetchShippingCompanies();
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0;
}

.avatar-uploader {
  .avatar {
    width: 200px;
    height: 60px;
    display: block;
    object-fit: contain;
    
    &.favicon {
      width: 32px;
      height: 32px;
    }
  }
  
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 200px;
    height: 60px;
    line-height: 60px;
    text-align: center;
  }
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.cert-uploader {
  .el-upload-list {
    margin-top: 10px;
  }
}
</style> 