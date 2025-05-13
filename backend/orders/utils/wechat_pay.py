import os
import time
import uuid
import hashlib
import xmltodict
import requests
from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode

class WechatPay:
    def __init__(self):
        self.app_id = settings.WECHAT_PAY['APP_ID']
        self.mch_id = settings.WECHAT_PAY['MCH_ID']
        self.api_key = settings.WECHAT_PAY['API_KEY']
        self.cert_path = settings.WECHAT_PAY['CERT_PATH']
        self.key_path = settings.WECHAT_PAY['KEY_PATH']
        self.notify_url = settings.WECHAT_PAY['NOTIFY_URL']
        self.unified_order_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        self.refund_url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        
    def _generate_nonce_str(self):
        """生成随机字符串"""
        return str(uuid.uuid4()).replace('-', '')
    
    def _generate_sign(self, data):
        """生成签名"""
        # 按字典序排序参数
        sign_list = []
        for k, v in sorted(data.items()):
            if k != 'sign' and v:  # 不参与签名
                sign_list.append(f'{k}={v}')
        # 拼接API密钥
        sign_list.append(f'key={self.api_key}')
        sign_str = '&'.join(sign_list)
        # MD5加密
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    def _dict_to_xml(self, data):
        """字典转XML"""
        xml_list = ['<xml>']
        for k, v in data.items():
            xml_list.append(f'<{k}>{v}</{k}>')
        xml_list.append('</xml>')
        return ''.join(xml_list)
    
    def _xml_to_dict(self, xml_str):
        """XML转字典"""
        return xmltodict.parse(xml_str)['xml']
    
    def create_order(self, order_number, total_fee, description, openid):
        """创建支付订单"""
        # 构造请求参数
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'body': description,
            'out_trade_no': order_number,
            'total_fee': total_fee,  # 单位：分
            'spbill_create_ip': '127.0.0.1',  # 可以填写服务器IP
            'notify_url': self.notify_url,
            'trade_type': 'JSAPI',  # 小程序支付
            'openid': openid
        }
        # 生成签名
        data['sign'] = self._generate_sign(data)
        # 转换为XML
        xml_data = self._dict_to_xml(data)
        # 发送请求
        response = requests.post(self.unified_order_url, data=xml_data.encode('utf-8'))
        # 解析响应
        result = self._xml_to_dict(response.content)
        
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            # 生成支付参数
            time_stamp = str(int(time.time()))
            pay_data = {
                'appId': self.app_id,
                'timeStamp': time_stamp,
                'nonceStr': self._generate_nonce_str(),
                'package': f'prepay_id={result["prepay_id"]}',
                'signType': 'MD5'
            }
            pay_data['paySign'] = self._generate_sign(pay_data)
            return pay_data
        else:
            raise Exception(result.get('return_msg') or result.get('err_code_des'))
    
    def verify_notify(self, xml_data):
        """验证支付回调"""
        # 解析XML数据
        data = self._xml_to_dict(xml_data)
        # 验证签名
        sign = data.pop('sign')
        if self._generate_sign(data) != sign:
            return False, None
        return True, data
    
    def create_refund(self, order_number, refund_number, total_fee, refund_fee):
        """申请退款"""
        # 构造请求参数
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'out_trade_no': order_number,
            'out_refund_no': refund_number,
            'total_fee': total_fee,  # 单位：分
            'refund_fee': refund_fee,  # 单位：分
        }
        # 生成签名
        data['sign'] = self._generate_sign(data)
        # 转换为XML
        xml_data = self._dict_to_xml(data)
        # 发送请求（需要证书）
        response = requests.post(
            self.refund_url,
            data=xml_data.encode('utf-8'),
            cert=(self.cert_path, self.key_path)
        )
        # 解析响应
        result = self._xml_to_dict(response.content)
        
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            return result
        else:
            raise Exception(result.get('return_msg') or result.get('err_code_des')) 