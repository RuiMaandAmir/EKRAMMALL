from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, DistributorProfile
from products.models import Category, Product
from orders.models import Order
from promotions.models import DistributionLink, DistributionLevel
from analytics.models import DataPoint, Report, Dashboard, Alert, UserBehavior, SalesAnalytics, UserAnalytics, ProductAnalytics
from django.contrib.contenttypes.models import ContentType
import json

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 创建测试用户
        self.user = User.objects.create_user(username='testuser', password='testpass123', is_distributor=True)
        # 创建测试管理员
        self.admin = User.objects.create_superuser(username='admin', password='adminpass123', email='admin@example.com')
        # 创建测试分类
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.category2 = Category.objects.create(name='Test Category 2', slug='test-category-2')
        self.category3 = Category.objects.create(name='Test Category 3', slug='test-category-3')
        self.category4 = Category.objects.create(name='Test Category 4', slug='test-category-4')
        # 创建测试商品
        self.product = Product.objects.create(name='Test Product', slug='test-product', price=100, stock=10)
        self.product.categories.add(self.category)
        # 创建测试订单
        self.order = Order.objects.create(user=self.user, total_amount=100, payment_amount=100, status='pending')
        
        # 创建分销商等级
        self.distribution_level = DistributionLevel.objects.create(
            name='初级分销商',
            level=1,
            commission_rate=0.05,
            second_level_rate=0.02
        )
        
        # 确保分销商资料存在
        self.distributor_profile = DistributorProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'commission_rate': 0.05,
                'level': self.distribution_level
            }
        )[0]
        
        # 创建测试分销链接
        self.distribution_link = DistributionLink.objects.create(
            distributor=self.distributor_profile,
            product=self.product,
            code='TEST123'
        )
        
        # 创建测试数据点
        self.data_point = DataPoint.objects.create(name='Test Data', value=100, category='test')
        # 创建测试报表
        self.report = Report.objects.create(name='Test Report', description='Test Description', query='SELECT * FROM test')
        # 创建测试仪表盘
        self.dashboard = Dashboard.objects.create(name='Test Dashboard', description='Test Description', layout='{}', created_by=self.user)
        # 创建测试告警
        self.alert = Alert.objects.create(name='Test Alert', description='Test Description', condition='value > 100', threshold=100)
        # 创建测试用户行为
        content_type = ContentType.objects.get_for_model(Product)
        self.user_behavior = UserBehavior.objects.create(user=self.user, action='test_action', content_type=content_type, object_id=self.product.id)
        # 创建测试销售分析
        self.sales_analytics = SalesAnalytics.objects.create(date='2023-01-01', total_sales=1000, order_count=10, average_order_value=100, product_count=1, customer_count=1)
        # 创建测试用户分析
        self.user_analytics = UserAnalytics.objects.create(date='2023-01-01', new_users=5, active_users=10, returning_users=2, churned_users=1, total_users=10, user_segments={})
        # 创建测试商品分析
        self.product_analytics = ProductAnalytics.objects.create(
            date='2023-01-01', 
            product=self.product, 
            views=100, 
            sales=10,
            revenue=1000.00,
            conversion_rate=0.1,
            average_rating=4.5,
            review_count=5
        )

    def test_user_registration(self):
        url = reverse('user-register')
        data = {'username': 'newuser', 'password': 'newpass123', 'email': 'newuser@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        url = reverse('user-login')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_category_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('products:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_product_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_order_creation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order-list')
        data = {
            'total_amount': 200,
            'payment_amount': 200,
            'status': 'pending',
            'recipient_name': '张三',
            'recipient_phone': '13800000000',
            'recipient_address': '测试地址',
            'shipping_method': '快递',
            'payment_method': '微信',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(total_amount=200).exists())

    def test_distribution_link_generation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('products:generate_distribution_link', kwargs={'product_id': self.product.id})
        response = self.client.post(url, {'product_id': self.product.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('code', response.data)

    def test_data_point_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('datapoint-list')
        data = {'name': 'New Data', 'value': 200, 'category': 'new'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DataPoint.objects.filter(name='New Data').exists())

    def test_report_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('report-list')
        data = {'name': 'New Report', 'description': 'New Description', 'query': 'SELECT * FROM new'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Report.objects.filter(name='New Report').exists())

    def test_dashboard_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('dashboard-list')
        data = {'name': 'New Dashboard', 'description': 'New Description', 'layout': '{}'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Dashboard.objects.filter(name='New Dashboard').exists())

    def test_alert_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('alert-list')
        data = {'name': 'New Alert', 'description': 'New Description', 'condition': 'value > 200', 'threshold': 200}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Alert.objects.filter(name='New Alert').exists())

    def test_user_behavior_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('userbehavior-list')
        from django.contrib.contenttypes.models import ContentType
        product_content_type = ContentType.objects.get_for_model(Product)
        data = {'user': self.admin.id, 'action': 'new_action', 'content_type': product_content_type.id, 'object_id': self.product.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserBehavior.objects.filter(action='new_action').exists())

    def test_sales_analytics_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('salesanalytics-list')
        data = {'date': '2023-01-02', 'total_sales': 2000, 'order_count': 20}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SalesAnalytics.objects.filter(date='2023-01-02').exists())

    def test_user_analytics_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('useranalytics-list')
        data = {'date': '2023-01-02', 'new_users': 10, 'active_users': 20}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserAnalytics.objects.filter(date='2023-01-02').exists())

    def test_product_analytics_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('productanalytics-list')
        data = {'date': '2023-01-02', 'product': self.product.id, 'views': 200, 'sales': 20}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductAnalytics.objects.filter(date='2023-01-02').exists())

    # 权限测试
    def test_user_permission(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_permission(self):
        url = reverse('user-list')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_permission(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_permission(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_distribution_permission(self):
        url = reverse('distributionlink-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_permission(self):
        url = reverse('datapoint-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 生成测试报告
    def tearDown(self):
        with open('test_report.json', 'w') as f:
            json.dump({
                'user_registration': self.test_user_registration.__name__,
                'user_login': self.test_user_login.__name__,
                'category_list': self.test_category_list.__name__,
                'product_detail': self.test_product_detail.__name__,
                'order_creation': self.test_order_creation.__name__,
                'distribution_link_generation': self.test_distribution_link_generation.__name__,
                'data_point_creation': self.test_data_point_creation.__name__,
                'report_creation': self.test_report_creation.__name__,
                'dashboard_creation': self.test_dashboard_creation.__name__,
                'alert_creation': self.test_alert_creation.__name__,
                'user_behavior_creation': self.test_user_behavior_creation.__name__,
                'sales_analytics_creation': self.test_sales_analytics_creation.__name__,
                'user_analytics_creation': self.test_user_analytics_creation.__name__,
                'product_analytics_creation': self.test_product_analytics_creation.__name__,
                'user_permission': self.test_user_permission.__name__,
                'admin_permission': self.test_admin_permission.__name__,
                'product_permission': self.test_product_permission.__name__,
                'order_permission': self.test_order_permission.__name__,
                'distribution_permission': self.test_distribution_permission.__name__,
                'analytics_permission': self.test_analytics_permission.__name__,
            }, f, indent=4) 