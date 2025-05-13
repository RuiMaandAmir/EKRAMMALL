from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Advertisement
from .serializers import AdvertisementSerializer

# Create your views here.

class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前有效的广告"""
        now = timezone.now()
        ad = Advertisement.objects.filter(
            status=True,
            start_time__lte=now,
            end_time__gte=now
        ).order_by('-created_at').first()

        if not ad:
            return Response({'data': None})

        serializer = self.get_serializer(ad)
        return Response({
            'data': {
                'id': ad.id,
                'title': ad.title,
                'imageUrl': request.build_absolute_uri(ad.image.url),
                'linkUrl': ad.link_url,
                'allowClose': ad.allow_close
            }
        })
