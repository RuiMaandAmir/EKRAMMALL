from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import Category, Product, ProductVariant, ProductImage, ProductSpecification, ProductReview, ReviewReply
from promotions.models import DistributionLink
from .serializers import (
    CategorySerializer, ProductSerializer, ProductVariantSerializer,
    ProductImageSerializer, ProductSpecificationSerializer, ProductDetailSerializer,
    ProductReviewSerializer, ProductReviewCreateSerializer, ReviewReplySerializer
)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from accounts.models import DistributorProfile
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    商品分类视图集
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'created_at']
    
    def get_queryset(self):
        queryset = Category.objects.all()
        if self.action == 'list':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def perform_destroy(self, instance):
        # 软删除
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        获取分类下的商品
        """
        category = self.get_object()
        products = category.get_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """
        获取子分类
        """
        category = self.get_object()
        children = category.get_children()
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def breadcrumbs(self, request, pk=None):
        """
        获取面包屑导航
        """
        category = self.get_object()
        breadcrumbs = category.get_breadcrumbs()
        return Response(breadcrumbs)

class CategoryTreeView(APIView):
    """
    获取分类树
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        def get_category_tree(category):
            children = []
            for child in category.get_children():
                children.append(get_category_tree(child))
            
            return {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'image_url': category.image.url if category.image else None,
                'product_count': category.get_products().count(),
                'children': children
            }
        
        # 获取顶级分类
        top_categories = Category.objects.filter(parent=None, is_active=True)
        tree = []
        for category in top_categories:
            tree.append(get_category_tree(category))
        
        return Response(tree)

def product_detail(request, slug):
    """
    产品详情页
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    context = {
        'product': product,
        'variants': product.variants.filter(is_active=True),
        'images': product.images.all(),
    }
    
    # 如果用户是分销商，生成分销链接
    if request.user.is_authenticated and request.user.is_distributor:
        distributor = request.user.distributor_profile
        distribution_link = DistributionLink.objects.get_or_create(
            distributor=distributor,
            product=product
        )[0]
        context['distribution_link'] = distribution_link
    
    return render(request, 'products/product_detail.html', context)

class GenerateDistributionLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        if not request.user.is_distributor:
            return Response({
                'status': 'error',
                'message': '只有分销商才能生成分销链接'
            }, status=403)
        product = get_object_or_404(Product, id=product_id)
        distributor = request.user.distributor_profile
        if not product.allow_distribution:
            return Response({
                'status': 'error',
                'message': '该产品不允许分销'
            }, status=400)
        distribution_link = DistributionLink.objects.get_or_create(
            distributor=distributor,
            product=product
        )[0]
        distribution_link.click_count += 1
        distribution_link.save()
        return Response({
            'status': 'success',
            'link': f"/product/{product.slug}?ref={distribution_link.code}",
            'code': distribution_link.code
        })

    def post(self, request, product_id):
        if not request.user.is_distributor:
            return Response({
                'status': 'error',
                'message': '只有分销商才能生成分销链接'
            }, status=403)
        product = get_object_or_404(Product, id=product_id)
        distributor = request.user.distributor_profile
        if not product.allow_distribution:
            return Response({
                'status': 'error',
                'message': '该产品不允许分销'
            }, status=400)
        distribution_link = DistributionLink.objects.get_or_create(
            distributor=distributor,
            product=product
        )[0]
        distribution_link.click_count += 1
        distribution_link.save()
        return Response({
            'status': 'success',
            'link': f"/product/{product.slug}?ref={distribution_link.code}",
            'code': distribution_link.code
        })

class ProductViewSet(viewsets.ModelViewSet):
    """商品视图集"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sales', 'created_at']

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images', 'specifications')
        if self.action == 'list':
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """切换商品推荐状态"""
        product = self.get_object()
        product.is_featured = not product.is_featured
        product.save()
        return Response({'is_featured': product.is_featured})

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换商品上下架状态"""
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        return Response({'is_active': product.is_active})

class ProductImageViewSet(viewsets.ModelViewSet):
    """商品图片视图集"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs['product_pk'])

class ProductSpecificationViewSet(viewsets.ModelViewSet):
    """商品规格视图集"""
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductSpecification.objects.filter(product_id=self.kwargs['product_pk'])

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs['product_pk'])

class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class ProductReviewViewSet(viewsets.ModelViewSet):
    """商品评价视图集"""
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['product', 'rating', 'is_verified']
    search_fields = ['content']
    ordering_fields = ['created_at', 'rating', 'likes']
    ordering = ['-created_at']
    pagination_class = ReviewPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductReviewCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞评价"""
        review = self.get_object()
        review.likes += 1
        review.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """回复评价"""
        review = self.get_object()
        serializer = ReviewReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, review=review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewReplyViewSet(viewsets.ModelViewSet):
    """评价回复视图集"""
    queryset = ReviewReply.objects.all()
    serializer_class = ReviewReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['review']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    pagination_class = ReviewPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
