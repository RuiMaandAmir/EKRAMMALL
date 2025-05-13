import hashlib
import time
import random
import string
import requests
from django.conf import settings

class WechatPay:
    def __init__(self):
        self.appid = settings.WECHAT_APPID
        self.mch_id = settings.WECHAT_MCH_ID
        self.api_key = settings.WECHAT_API_KEY
        self.notify_url = settings.WECHAT_NOTIFY_URL
    
    def _generate_nonce_str(self, length=32):
        """生成随机字符串"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    def _generate_sign(self, params):
        """生成签名"""
        # 按字典序排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 拼接字符串
        stringA = '&'.join([f"{k}={v}" for k, v in sorted_params])
        # 拼接API密钥
        stringSignTemp = f"{stringA}&key={self.api_key}"
        # MD5加密
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
        return sign
    
    def create_order(self, order_number, amount, description):
        """创建订单"""
        # 构建参数
        params = {
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'body': description,
            'out_trade_no': order_number,
            'total_fee': int(amount * 100),  # 转换为分
            'spbill_create_ip': '127.0.0.1',  # 实际使用时需要获取用户IP
            'notify_url': self.notify_url,
            'trade_type': 'JSAPI'  # 小程序支付
        }
        
        # 生成签名
        params['sign'] = self._generate_sign(params)
        
        # 发送请求
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        response = requests.post(url, data=self._dict_to_xml(params))
        result = self._xml_to_dict(response.text)
        
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            # 生成小程序支付参数
            pay_params = {
                'appId': self.appid,
                'timeStamp': str(int(time.time())),
                'nonceStr': self._generate_nonce_str(),
                'package': f"prepay_id={result['prepay_id']}",
                'signType': 'MD5'
            }
            pay_params['paySign'] = self._generate_sign(pay_params)
            return pay_params
        
        raise Exception(result.get('return_msg', '创建订单失败'))
    
    def create_refund(self, transaction_id, refund_id, amount, reason):
        """创建退款"""
        # 构建参数
        params = {
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'transaction_id': transaction_id,
            'out_refund_no': refund_id,
            'total_fee': int(amount * 100),  # 转换为分
            'refund_fee': int(amount * 100),  # 转换为分
            'refund_desc': reason
        }
        
        # 生成签名
        params['sign'] = self._generate_sign(params)
        
        # 发送请求
        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        response = requests.post(url, data=self._dict_to_xml(params))
        result = self._xml_to_dict(response.text)
        
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            return result
        
        raise Exception(result.get('return_msg', '创建退款失败'))
    
    def verify_notify(self, data):
        """验证回调数据"""
        # 验证签名
        sign = data.pop('sign', '')
        if sign != self._generate_sign(data):
            return {'success': False, 'message': '签名验证失败'}
        
        if data['return_code'] == 'SUCCESS' and data['result_code'] == 'SUCCESS':
            return {
                'success': True,
                'transaction_id': data['transaction_id'],
                'out_trade_no': data['out_trade_no']
            }
        
        return {'success': False, 'message': data.get('return_msg', '支付失败')}
    
    def _dict_to_xml(self, params):
        """字典转XML"""
        xml = ['<xml>']
        for k, v in params.items():
            xml.append(f'<{k}>{v}</{k}>')
        xml.append('</xml>')
        return ''.join(xml)
    
    def _xml_to_dict(self, xml):
        """XML转字典"""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result 