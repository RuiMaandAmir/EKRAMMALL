import hashlib
import time
import uuid
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WechatPay:
    """微信支付工具类"""
    
    def __init__(self):
        self.mch_id = settings.WECHAT_PAY['MCH_ID']
        self.api_key = settings.WECHAT_PAY['API_KEY']
        self.app_id = settings.WECHAT_PAY['APP_ID']
        self.cert_path = settings.WECHAT_PAY['CERT_PATH']
        self.key_path = settings.WECHAT_PAY['KEY_PATH']
        
    def _generate_nonce_str(self):
        """生成随机字符串"""
        return str(uuid.uuid4()).replace('-', '')
        
    def _generate_sign(self, data):
        """生成签名"""
        # 按字典序排序
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        # 拼接字符串
        sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
        # 加入商户密钥
        sign_str += f'&key={self.api_key}'
        # MD5加密
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
        
    def transfer_to_balance(self, openid, amount, desc):
        """
        企业付款到零钱
        
        :param openid: 接收者的openid
        :param amount: 金额（单位：分）
        :param desc: 企业付款描述
        :return: 返回结果
        """
        url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'
        
        data = {
            'mch_appid': self.app_id,
            'mchid': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'partner_trade_no': f'WD{int(time.time())}{uuid.uuid4().hex[:8]}',
            'openid': openid,
            'check_name': 'NO_CHECK',  # 不校验真实姓名
            'amount': amount,
            'desc': desc,
            'spbill_create_ip': '127.0.0.1'
        }
        
        # 生成签名
        data['sign'] = self._generate_sign(data)
        
        try:
            # 发送请求
            response = requests.post(
                url,
                data=data,
                cert=(self.cert_path, self.key_path),
                verify=True
            )
            
            # 解析响应
            result = response.json()
            logger.info(f'微信企业付款结果: {result}')
            
            return result
            
        except Exception as e:
            logger.error(f'微信企业付款异常: {str(e)}')
            raise 