from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Banner, Navigation, HomeLayout, SpecialPage,
    BannerItem, NavigationItem, LayoutSection
)
from .serializers import (
    BannerSerializer, NavigationSerializer, HomeLayoutSerializer, SpecialPageSerializer,
    BannerItemSerializer, NavigationItemSerializer, LayoutSectionSerializer
)

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        banner = self.get_object()
        items = banner.items.all()
        serializer = BannerItemSerializer(items, many=True)
        return Response(serializer.data)

class NavigationViewSet(viewsets.ModelViewSet):
    queryset = Navigation.objects.all()
    serializer_class = NavigationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        navigation = self.get_object()
        items = navigation.items.all()
        serializer = NavigationItemSerializer(items, many=True)
        return Response(serializer.data)

class HomeLayoutViewSet(viewsets.ModelViewSet):
    queryset = HomeLayout.objects.all()
    serializer_class = HomeLayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        layout = self.get_object()
        sections = layout.sections.all()
        serializer = LayoutSectionSerializer(sections, many=True)
        return Response(serializer.data)

class SpecialPageViewSet(viewsets.ModelViewSet):
    queryset = SpecialPage.objects.all()
    serializer_class = SpecialPageSerializer
    permission_classes = [permissions.IsAuthenticated] 