from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
import datetime
from django.db.models import Q

from .models import Order, OrderItem, Cart, CartItem, Payment, Refund
from .serializers import (
    OrderSerializer, OrderItemSerializer, CartSerializer,
    CartItemSerializer, ApplyDistributorCodeSerializer,
    PaymentSerializer, RefundSerializer, CreatePaymentSerializer, CreateRefundSerializer
)
from products.models import Product, ProductVariant
from accounts.models import DistributorProfile
from promotions.models import DistributionLink
from .utils.wechat_pay import WechatPay

class OrderViewSet(viewsets.ModelViewSet):
    """
    订单视图集
    """
    queryset = Order.objects.all()  # 添加queryset属性
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        根据用户角色返回不同的查询集：
        - 管理员可以看到所有订单
        - 普通用户只能看到自己的订单
        - 分销商可以看到通过自己分销链接产生的订单
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        elif hasattr(user, 'distributor_profile'):
            return Order.objects.filter(
                Q(distributor=user.distributor_profile) |
                Q(parent_distributor=user.distributor_profile) |
                Q(user=user)
            ).distinct()
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        创建订单时自动设置用户
        """
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        """
        为序列化器提供额外的上下文
        """
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

class ApplyDistributorCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = ApplyDistributorCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        
        try:
            link = DistributionLink.objects.get(code=code, is_active=True)
        except DistributionLink.DoesNotExist:
            return Response({"error": "分销码无效"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新购物车的分销码
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.distribution_code = code
        cart.save()
        
        # 更新分享次数
        link.share_count += 1
        link.save()
        
        return Response({
            "message": "分销码应用成功",
            "distributor": {
                "id": link.distributor.id,
                "username": link.distributor.user.username
            }
        })

class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # 获取购物车
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "购物车为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查购物车是否为空
        if not cart.items.exists():
            return Response({"error": "购物车为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建订单
        order = Order.objects.create(
            user=request.user,
            status='pending',
            total_amount=cart.total_amount,
            payment_amount=cart.total_amount,
            distribution_code=cart.distribution_code,
            recipient_name=request.data.get('recipient_name'),
            recipient_phone=request.data.get('recipient_phone'),
            recipient_address=request.data.get('recipient_address')
        )
        
        # 设置分销商信息
        if cart.distribution_code:
            try:
                link = DistributionLink.objects.get(code=cart.distribution_code)
                order.distributor = link.distributor
                if link.distributor.parent:
                    order.parent_distributor = link.distributor.parent
                order.save()
            except DistributionLink.DoesNotExist:
                pass
        
        # 创建订单项
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.price,
                subtotal=item.subtotal
            )
        
        # 清空购物车
        cart.items.all().delete()
        cart.distribution_code = None
        cart.save()
        
        return Response({
            "message": "订单创建成功",
            "order": OrderSerializer(order).data
        })

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()  # 添加queryset属性
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)

class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()  # 添加queryset属性
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(order__user=self.request.user)

class PaymentCallbackView(APIView):
    """
    处理微信支付回调
    """
    def post(self, request, *args, **kwargs):
        wechat_pay = WechatPay()
        # 获取原始的XML数据
        xml_data = request.body
        
        try:
            # 验证签名
            is_valid, data = wechat_pay.verify_notify(xml_data)
            if not is_valid:
                return Response({'return_code': 'FAIL', 'return_msg': '签名验证失败'})
            
            # 验证支付结果
            if data['return_code'] != 'SUCCESS' or data['result_code'] != 'SUCCESS':
                return Response({'return_code': 'FAIL', 'return_msg': '支付失败'})
            
            # 获取订单信息
            order_number = data['out_trade_no']
            transaction_id = data['transaction_id']
            total_fee = int(data['total_fee'])
            
            try:
                order = Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                return Response({'return_code': 'FAIL', 'return_msg': '订单不存在'})
            
            # 验证金额
            if total_fee != int(order.payment_amount * 100):  # 转换为分
                return Response({'return_code': 'FAIL', 'return_msg': '支付金额不匹配'})
            
            # 更新支付记录
            payment = Payment.objects.create(
                order=order,
                payment_method='wechat',
                amount=order.payment_amount,
                status='success',
                transaction_id=transaction_id,
                payment_data=data
            )
            
            # 更新订单状态
            order.status = 'paid'
            order.payment_id = transaction_id
            order.paid_at = timezone.now()
            order.save()
            
            # 计算佣金
            order.calculate_commission()
            
            return Response({'return_code': 'SUCCESS', 'return_msg': 'OK'})
            
        except Exception as e:
            return Response({'return_code': 'FAIL', 'return_msg': str(e)})

class CreatePaymentView(APIView):
    """
    创建支付订单
    """
    def post(self, request, order_number, *args, **kwargs):
        try:
            order = Order.objects.get(order_number=order_number)
            
            # 检查订单状态
            if order.status != 'pending':
                return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查是否已有支付记录
            if Payment.objects.filter(order=order, status='success').exists():
                return Response({'error': '订单已支付'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取支付方式
            payment_method = request.data.get('payment_method')
            if not payment_method or payment_method not in ['wechat', 'alipay']:
                return Response({'error': '不支持的支付方式'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 根据支付方式创建支付订单
            if payment_method == 'wechat':
                wechat_pay = WechatPay()
                pay_data = wechat_pay.create_order(
                    order_number=order.order_number,
                    total_fee=int(order.payment_amount * 100),  # 转换为分
                    description=f'订单 {order.order_number}',
                    openid=request.user.wechat_openid
                )
            else:  # alipay
                from .utils.alipay_pay import AlipayPay
                alipay = AlipayPay()
                pay_data = alipay.create_order(
                    order_number=order.order_number,
                    total_fee=float(order.payment_amount),
                    description=f'订单 {order.order_number}',
                    return_url=request.data.get('return_url'),
                    notify_url=request.data.get('notify_url')
                )
            
            # 创建支付记录
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.payment_amount,
                status='pending'
            )
            
            return Response(pay_data)
            
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateRefundView(APIView):
    """
    创建退款申请
    """
    def post(self, request, order_number, *args, **kwargs):
        try:
            order = Order.objects.get(order_number=order_number)
            
            # 检查订单状态
            if order.status != 'paid':
                return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查是否已有退款记录
            if Refund.objects.filter(order=order).exists():
                return Response({'error': '订单已申请退款'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取支付记录
            payment = Payment.objects.filter(order=order, status='success').first()
            if not payment:
                return Response({'error': '未找到支付记录'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建退款记录
            refund = Refund.objects.create(
                order=order,
                payment=payment,
                amount=order.payment_amount,
                reason=request.data.get('reason', '用户申请退款')
            )
            
            # 申请微信退款
            wechat_pay = WechatPay()
            result = wechat_pay.create_refund(
                order_number=order.order_number,
                refund_number=f'RF{order.order_number}',
                total_fee=int(order.payment_amount * 100),  # 转换为分
                refund_fee=int(order.payment_amount * 100)  # 全额退款
            )
            
            # 更新退款记录
            refund.status = 'success'
            refund.refund_id = result['refund_id']
            refund.refund_data = result
            refund.save()
            
            # 更新订单状态
            order.status = 'refunded'
            order.save()
            
            return Response({'message': '退款申请成功'})
            
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AlipayCallbackView(APIView):
    """
    处理支付宝支付回调
    """
    def post(self, request, *args, **kwargs):
        from .utils.alipay_pay import AlipayPay
        alipay = AlipayPay()
        
        # 验证回调数据
        is_valid, data = alipay.verify_notify(request.POST.dict())
        if not is_valid:
            return Response('fail')
        
        try:
            # 获取订单信息
            order_number = data['out_trade_no']
            transaction_id = data['trade_no']
            
            order = Order.objects.get(order_number=order_number)
            
            # 更新支付记录
            payment = Payment.objects.create(
                order=order,
                payment_method='alipay',
                amount=order.payment_amount,
                status='success',
                transaction_id=transaction_id,
                payment_data=data
            )
            
            # 更新订单状态
            order.status = 'paid'
            order.payment_id = transaction_id
            order.paid_at = timezone.now()
            order.save()
            
            # 计算佣金
            order.calculate_commission()
            
            return Response('success')
            
        except Order.DoesNotExist:
            return Response('fail')
        except Exception as e:
            logger.error(f'支付宝回调处理异常: {str(e)}')
            return Response('fail')
