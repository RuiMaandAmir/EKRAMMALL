import hashlib
import time
import uuid
import requests
from django.conf import settings
import logging
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
import json

logger = logging.getLogger(__name__)

class AlipayPay:
    """支付宝支付工具类"""
    
    def __init__(self):
        self.app_id = settings.ALIPAY['APP_ID']
        self.merchant_private_key = settings.ALIPAY['MERCHANT_PRIVATE_KEY']
        self.alipay_public_key = settings.ALIPAY['ALIPAY_PUBLIC_KEY']
        self.notify_url = settings.ALIPAY['NOTIFY_URL']
        self.return_url = settings.ALIPAY['RETURN_URL']
        self.gateway = 'https://openapi.alipay.com/gateway.do'
        
    def _generate_sign(self, data):
        """生成签名"""
        # 按字典序排序
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        # 拼接字符串
        sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
        
        # 使用RSA2签名
        private_key = RSA.importKey(b64decode(self.merchant_private_key))
        signer = PKCS1_v1_5.new(private_key)
        hash_obj = SHA256.new(sign_str.encode('utf-8'))
        signature = b64encode(signer.sign(hash_obj)).decode('utf-8')
        
        return signature
        
    def _verify_sign(self, data, sign):
        """验证签名"""
        # 按字典序排序
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        # 拼接字符串
        sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
        
        # 使用RSA2验证签名
        public_key = RSA.importKey(b64decode(self.alipay_public_key))
        verifier = PKCS1_v1_5.new(public_key)
        hash_obj = SHA256.new(sign_str.encode('utf-8'))
        return verifier.verify(hash_obj, b64decode(sign))
        
    def create_order(self, order_number, total_fee, description, return_url=None, notify_url=None):
        """
        创建支付宝支付订单
        
        :param order_number: 订单号
        :param total_fee: 金额（单位：元）
        :param description: 订单描述
        :param return_url: 前端回跳地址
        :param notify_url: 后端回调地址
        :return: 支付参数
        """
        data = {
            'app_id': self.app_id,
            'method': 'alipay.trade.page.pay',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'notify_url': notify_url or self.notify_url,
            'return_url': return_url or self.return_url,
            'biz_content': json.dumps({
                'out_trade_no': order_number,
                'total_amount': str(total_fee),
                'subject': description,
                'product_code': 'FAST_INSTANT_TRADE_PAY'
            })
        }
        
        # 生成签名
        data['sign'] = self._generate_sign(data)
        
        # 构建支付链接
        pay_url = f"{self.gateway}?{'&'.join([f'{k}={v}' for k, v in data.items()])}"
        
        return {
            'pay_url': pay_url,
            'order_number': order_number
        }
        
    def verify_notify(self, data):
        """
        验证支付宝回调
        
        :param data: 回调数据
        :return: (是否验证通过, 回调数据)
        """
        try:
            # 验证签名
            sign = data.pop('sign')
            if not self._verify_sign(data, sign):
                return False, None
                
            # 验证app_id
            if data.get('app_id') != self.app_id:
                return False, None
                
            # 验证交易状态
            if data.get('trade_status') != 'TRADE_SUCCESS':
                return False, None
                
            return True, data
            
        except Exception as e:
            logger.error(f'支付宝回调验证异常: {str(e)}')
            return False, None
            
    def query_order(self, order_number):
        """
        查询订单状态
        
        :param order_number: 订单号
        :return: 订单信息
        """
        data = {
            'app_id': self.app_id,
            'method': 'alipay.trade.query',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps({
                'out_trade_no': order_number
            })
        }
        
        # 生成签名
        data['sign'] = self._generate_sign(data)
        
        try:
            response = requests.post(self.gateway, data=data)
            result = response.json()
            
            if result['alipay_trade_query_response']['code'] == '10000':
                return result['alipay_trade_query_response']
            return None
            
        except Exception as e:
            logger.error(f'查询订单异常: {str(e)}')
            return None 