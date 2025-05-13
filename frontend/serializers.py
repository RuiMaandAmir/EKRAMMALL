from rest_framework import serializers
from .models import (
    Banner, Navigation, HomeLayout, SpecialPage,
    BannerItem, NavigationItem, LayoutSection
)

class BannerItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerItem
        fields = ['id', 'title', 'image', 'link', 'sort_order', 'is_active']

class BannerSerializer(serializers.ModelSerializer):
    items = BannerItemSerializer(many=True, read_only=True)

    class Meta:
        model = Banner
        fields = ['id', 'name', 'position', 'is_active', 'items', 'created_at', 'updated_at']

class NavigationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationItem
        fields = ['id', 'title', 'link', 'icon', 'sort_order', 'is_active']

class NavigationSerializer(serializers.ModelSerializer):
    items = NavigationItemSerializer(many=True, read_only=True)

    class Meta:
        model = Navigation
        fields = ['id', 'name', 'position', 'is_active', 'items', 'created_at', 'updated_at']

class LayoutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayoutSection
        fields = ['id', 'title', 'type', 'content', 'sort_order', 'is_active']

class HomeLayoutSerializer(serializers.ModelSerializer):
    sections = LayoutSectionSerializer(many=True, read_only=True)

    class Meta:
        model = HomeLayout
        fields = ['id', 'name', 'is_active', 'sections', 'created_at', 'updated_at']

class SpecialPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialPage
        fields = ['id', 'title', 'slug', 'content', 'is_active', 'created_at', 'updated_at'] 