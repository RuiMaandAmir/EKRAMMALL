from decimal import Decimal
from django.db import transaction
from .models import DistributionLink, DistributionTeam
from apps.accounts.models import DistributorProfile, CommissionRecord
from orders.models import Order

class CommissionService:
    """佣金服务类"""
    
    @staticmethod
    @transaction.atomic
    def calculate_order_commission(order):
        """计算订单佣金"""
        # 获取分销链接
        link = DistributionLink.objects.filter(
            code=order.distribution_code
        ).first()
        
        if not link:
            return
        
        # 获取分销商
        distributor = link.distributor
        
        # 计算一级分销佣金
        first_level_amount = distributor.calculate_commission(
            order.total_amount,
            level=1
        )
        
        # 创建一级分销佣金记录
        CommissionRecord.objects.create(
            distributor=distributor,
            order=order,
            amount=first_level_amount,
            level=1
        )
        
        # 获取上级分销商
        team = DistributionTeam.objects.filter(
            distributor=distributor
        ).first()
        
        if team and team.parent:
            # 计算二级分销佣金
            second_level_amount = team.parent.calculate_commission(
                order.total_amount,
                level=2
            )
            
            # 创建二级分销佣金记录
            CommissionRecord.objects.create(
                distributor=team.parent,
                order=order,
                amount=second_level_amount,
                level=2
            )
    
    @staticmethod
    @transaction.atomic
    def freeze_pending_commissions():
        """冻结待结算佣金"""
        records = CommissionRecord.objects.filter(
            status='pending'
        ).select_related('distributor')
        
        for record in records:
            record.freeze()
    
    @staticmethod
    @transaction.atomic
    def unfreeze_commissions():
        """解冻佣金"""
        records = CommissionRecord.objects.filter(
            status='frozen'
        ).select_related('distributor')
        
        for record in records:
            record.unfreeze()
    
    @staticmethod
    @transaction.atomic
    def process_withdrawal(distributor, amount):
        """处理提现"""
        if distributor.available_commission < amount:
            raise ValueError('可提现佣金不足')
        
        # 创建提现记录
        records = CommissionRecord.objects.filter(
            distributor=distributor,
            status='available'
        ).order_by('created_at')
        
        remaining_amount = amount
        for record in records:
            if remaining_amount <= 0:
                break
            
            if record.amount <= remaining_amount:
                record.withdraw()
                remaining_amount -= record.amount
            else:
                # 拆分佣金记录
                new_record = CommissionRecord.objects.create(
                    distributor=distributor,
                    order=record.order,
                    amount=remaining_amount,
                    level=record.level,
                    status='available'
                )
                new_record.withdraw()
                
                record.amount -= remaining_amount
                record.save(update_fields=['amount'])
                remaining_amount = 0
    
    @staticmethod
    @transaction.atomic
    def cancel_order_commissions(order):
        """取消订单佣金"""
        records = CommissionRecord.objects.filter(
            order=order
        ).select_related('distributor')
        
        for record in records:
            record.cancel() 