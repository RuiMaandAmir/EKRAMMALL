from rest_framework.exceptions import APIException
from rest_framework import status

class CouponValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '优惠券验证失败'
    default_code = 'coupon_validation_error'

class CouponExpiredError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '优惠券已过期'
    default_code = 'coupon_expired'

class CouponUsedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '优惠券已被使用'
    default_code = 'coupon_used'

class CouponLimitError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '优惠券使用次数已达上限'
    default_code = 'coupon_limit_reached'

class ActivityValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '促销活动验证失败'
    default_code = 'activity_validation_error'

class ActivityTimeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '促销活动时间设置错误'
    default_code = 'activity_time_error'

class ProductStockError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '商品库存不足'
    default_code = 'product_stock_insufficient'

class PromotionPriceError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '促销价格设置错误'
    default_code = 'promotion_price_error' 