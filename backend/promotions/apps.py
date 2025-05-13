from django.apps import AppConfig


class PromotionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "promotions"
    verbose_name = "促销管理"

    def ready(self):
        try:
            from django.contrib.auth.models import Permission, Group
            from django.contrib.contenttypes.models import ContentType
            from .models import Coupon, PromotionActivity, PromotionProduct

            # 创建内容类型
            coupon_content_type = ContentType.objects.get_for_model(Coupon)
            activity_content_type = ContentType.objects.get_for_model(PromotionActivity)
            product_content_type = ContentType.objects.get_for_model(PromotionProduct)

            # 创建权限
            permissions = [
                ('manage_promotion', '管理促销活动'),
                ('manage_coupon', '管理优惠券'),
                ('manage_activity', '管理促销活动'),
                ('use_coupon', '使用优惠券'),
                ('view_promotion', '查看促销信息'),
            ]

            for codename, name in permissions:
                Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=coupon_content_type
                )

            # 为管理员组添加权限
            try:
                admin_group = Group.objects.get(name='admin')
                for codename, _ in permissions:
                    permission = Permission.objects.get(codename=codename)
                    admin_group.permissions.add(permission)
            except Group.DoesNotExist:
                pass
        except Exception as e:
            print(f"Warning: Could not initialize promotions app: {e}")
