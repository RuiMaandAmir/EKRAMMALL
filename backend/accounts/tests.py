from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import DistributorProfile, WithdrawalRecord

User = get_user_model()

class WithdrawalTests(TestCase):
    def setUp(self):
        # 创建管理员用户
        self.admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'password': 'admin123',
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if not self.admin.check_password('admin123'):
            self.admin.set_password('admin123')
            self.admin.save()
        
        # 创建分销商用户
        self.distributor_user, _ = User.objects.get_or_create(
            username='distributor',
            defaults={
                'password': 'distributor123',
                'email': 'distributor@example.com'
            }
        )
        if not self.distributor_user.check_password('distributor123'):
            self.distributor_user.set_password('distributor123')
            self.distributor_user.save()
        self.distributor, _ = DistributorProfile.objects.get_or_create(
            user=self.distributor_user,
            defaults={'balance': Decimal('1000.00')}
        )
        if self.distributor.balance != Decimal('1000.00'):
            self.distributor.balance = Decimal('1000.00')
            self.distributor.save()
        
        # 创建API客户端
        self.client = APIClient()
        
        # 强制刷新分销商对象，确保余额同步
        self.distributor.refresh_from_db()
        print("setUp distributor.balance:", self.distributor.balance)
        
    def test_withdrawal_creation(self):
        """测试提现申请创建"""
        # 登录分销商
        self.client.force_authenticate(user=self.distributor_user)
        
        # 创建提现申请
        data = {
            'amount': '100.00',
            'bank_name': '中国银行',
            'bank_account': '6222021234567890123',
            'account_holder': '张三'
        }
        response = self.client.post('/api/withdrawals/', data)
        print("response.data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证余额已冻结
        self.distributor.refresh_from_db()
        self.assertEqual(self.distributor.balance, Decimal('900.00'))
        
    def test_withdrawal_approval(self):
        """测试提现申请审批"""
        # 创建提现申请
        withdrawal = WithdrawalRecord.objects.create(
            distributor=self.distributor,
            amount=Decimal('100.00'),
            bank_name='中国银行',
            bank_account='6222021234567890123',
            account_holder='张三'
        )
        
        # 登录管理员
        self.client.force_authenticate(user=self.admin)
        
        # 批准提现
        response = self.client.post(f'/api/withdrawals/{withdrawal.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证状态已更新
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, 'approved')
        
    def test_withdrawal_rejection(self):
        """测试提现申请拒绝"""
        # 创建提现申请
        withdrawal = WithdrawalRecord.objects.create(
            distributor=self.distributor,
            amount=Decimal('100.00'),
            bank_name='中国银行',
            bank_account='6222021234567890123',
            account_holder='张三'
        )
        
        # 登录管理员
        self.client.force_authenticate(user=self.admin)
        
        # 拒绝提现
        data = {'reason': '银行账号信息不完整'}
        response = self.client.post(f'/api/withdrawals/{withdrawal.id}/reject/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证状态已更新且余额已返还
        withdrawal.refresh_from_db()
        self.distributor.refresh_from_db()
        self.assertEqual(withdrawal.status, 'rejected')
        self.assertEqual(self.distributor.balance, Decimal('1000.00'))
        
    def test_withdrawal_completion(self):
        """测试提现完成"""
        # 创建已批准的提现申请
        withdrawal = WithdrawalRecord.objects.create(
            distributor=self.distributor,
            amount=Decimal('100.00'),
            bank_name='中国银行',
            bank_account='6222021234567890123',
            account_holder='张三',
            status='approved'
        )
        
        # 登录管理员
        self.client.force_authenticate(user=self.admin)
        
        # 完成提现
        response = self.client.post(f'/api/withdrawals/{withdrawal.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证状态已更新
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, 'completed')
        
    def test_withdrawal_validation(self):
        """测试提现验证"""
        # 登录分销商
        self.client.force_authenticate(user=self.distributor_user)
        
        # 测试金额不足
        data = {
            'amount': '2000.00',  # 超过余额
            'bank_name': '中国银行',
            'bank_account': '6222021234567890123',
            'account_holder': '张三'
        }
        response = self.client.post('/api/withdrawals/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 测试最小金额
        data['amount'] = '5.00'  # 低于最小提现金额
        response = self.client.post('/api/withdrawals/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
