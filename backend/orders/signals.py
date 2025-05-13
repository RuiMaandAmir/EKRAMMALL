from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderLog

@receiver(post_save, sender=Order)
def create_order_log(sender, instance, created, **kwargs):
    """
    当订单状态改变时，创建订单日志
    """
    if created:
        OrderLog.objects.create(
            order=instance,
            status=instance.status,
            remark='订单创建'
        )
    else:
        # 获取原始订单状态
        original = Order.objects.get(pk=instance.pk)
        if original.status != instance.status:
            OrderLog.objects.create(
                order=instance,
                status=instance.status,
                remark=f'订单状态从{original.get_status_display()}变更为{instance.get_status_display()}'
            ) 