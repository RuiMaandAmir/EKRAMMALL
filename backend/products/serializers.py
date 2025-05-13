from rest_framework import serializers
from .models import Category, Product, ProductVariant, ProductImage, ProductSpecification, ReviewReply, ProductReview
from orders.models import OrderItem
from django.utils.translation import gettext_lazy as _
from accounts.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'description', 'image', 'order', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_children(self, obj):
        children = obj.get_children()
        return CategorySerializer(children, many=True).data
    
    def get_product_count(self, obj):
        return obj.get_products().count()
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'parent', 'description',
            'image', 'is_active', 'sort_order'
        ]
    
    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError("该URL标识已存在")
        return value

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'parent', 'description',
            'image', 'is_active', 'sort_order'
        ]
    
    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("该URL标识已存在")
        return value

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary', 'order')
        read_only_fields = ('id',)

class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('id', 'name', 'value', 'price_adjustment', 'stock')
        read_only_fields = ('id',)

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'category', 'category_name', 'description',
            'price', 'original_price', 'stock', 'sales',
            'is_active', 'is_featured', 'commission_rate',
            'images', 'specifications', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'sales')

    def validate(self, data):
        if data.get('price', 0) > data.get('original_price', 0):
            raise serializers.ValidationError("销售价格不能高于原价")
        return data

class ProductDetailSerializer(ProductSerializer):
    """商品详情序列化器"""
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ('description',)

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ReviewReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ReviewReply
        fields = ['id', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'content', 'images', 
                 'is_anonymous', 'is_verified', 'likes', 'replies',
                 'created_at', 'updated_at']
        read_only_fields = ['user', 'is_verified', 'likes', 'created_at', 'updated_at']
    
    def validate(self, data):
        # 验证用户是否购买过该商品
        if not OrderItem.objects.filter(
            order__user=self.context['request'].user,
            product_variant__product=data['product'],
            order__status='completed'
        ).exists():
            raise serializers.ValidationError(_('只有购买过该商品的用户才能评价'))
        return data

class ProductReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['product', 'rating', 'content', 'images', 'is_anonymous'] 