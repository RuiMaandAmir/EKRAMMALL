from django.core.exceptions import ValidationError
from django.utils import timezone
from .exceptions import (
    CouponValidationError, CouponExpiredError, CouponUsedError,
    CouponLimitError, ActivityValidationError, ActivityTimeError,
    ProductStockError, PromotionPriceError
)

def validate_coupon_usage(coupon, user, order):
    """验证优惠券使用条件"""
    try:
        # 检查优惠券是否有效
        if not coupon.is_active:
            raise CouponValidationError('优惠券已失效')
        
        # 检查使用时间
        now = timezone.now()
        if coupon.start_date and now < coupon.start_date:
            raise CouponValidationError('优惠券未到使用时间')
        if coupon.end_date and now > coupon.end_date:
            raise CouponExpiredError()
        
        # 检查使用次数
        if coupon.used_count >= coupon.quantity:
            raise CouponLimitError()
        
        # 检查最低消费
        if order.total_amount < coupon.min_purchase:
            raise CouponValidationError(f'订单金额未达到最低消费要求（{coupon.min_purchase}元）')
        
        # 检查用户是否已使用过
        if coupon.one_per_user and coupon.usages.filter(user=user).exists():
            raise CouponUsedError()
        
        # 检查优惠券是否适用于当前商品
        if coupon.products.exists() and not order.items.filter(product__in=coupon.products.all()).exists():
            raise CouponValidationError('优惠券不适用于当前商品')
        
        return True
    except ValidationError as e:
        raise CouponValidationError(str(e))

def validate_promotion_activity(activity):
    """验证促销活动"""
    try:
        # 检查活动时间
        now = timezone.now()
        if activity.start_date and now < activity.start_date:
            raise ActivityTimeError('活动未开始')
        if activity.end_date and now > activity.end_date:
            raise ActivityTimeError('活动已结束')
        
        # 检查活动状态
        if not activity.is_active:
            raise ActivityValidationError('活动已暂停')
        
        # 检查活动时间设置
        if activity.start_date and activity.end_date and activity.start_date >= activity.end_date:
            raise ActivityTimeError('活动开始时间不能晚于结束时间')
        
        return True
    except ValidationError as e:
        raise ActivityValidationError(str(e))

def validate_promotion_product(product, quantity):
    """验证促销商品"""
    try:
        # 检查库存
        if product.stock < quantity:
            raise ProductStockError()
        
        # 检查活动状态
        if not product.activity.is_active:
            raise ActivityValidationError('促销活动已结束')
        
        # 检查活动时间
        now = timezone.now()
        if product.activity.start_date and now < product.activity.start_date:
            raise ActivityTimeError('促销活动未开始')
        if product.activity.end_date and now > product.activity.end_date:
            raise ActivityTimeError('促销活动已结束')
        
        # 检查促销价格
        if product.promotion_price >= product.product.price:
            raise PromotionPriceError('促销价格不能高于原价')
        if product.promotion_price <= 0:
            raise PromotionPriceError('促销价格必须大于0')
        
        return True
    except ValidationError as e:
        raise ActivityValidationError(str(e))

def validate_coupon_data(data):
    """验证优惠券数据"""
    try:
        # 检查优惠类型和优惠值
        if data['discount_type'] == 'fixed' and data['discount_value'] <= 0:
            raise CouponValidationError('固定金额优惠必须大于0')
        if data['discount_type'] == 'percentage' and (data['discount_value'] <= 0 or data['discount_value'] > 100):
            raise CouponValidationError('百分比优惠必须在0-100之间')
        
        # 检查有效期
        if data['start_date'] and data['end_date'] and data['start_date'] >= data['end_date']:
            raise CouponValidationError('优惠券开始时间不能晚于结束时间')
        
        # 检查发放数量
        if data['quantity'] <= 0:
            raise CouponValidationError('发放数量必须大于0')
        
        return True
    except ValidationError as e:
        raise CouponValidationError(str(e)) 