from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import WorkOrder


class WorkOrderListPaginationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='pass1234')

    def test_active_work_orders_do_not_show_empty_second_page(self):
        WorkOrder.objects.create(title='First', description='One', category='Maintenance', priority='high', status='open', created_by=self.user)
        WorkOrder.objects.create(title='Second', description='Two', category='Maintenance', priority='medium', status='in_progress', created_by=self.user)
        WorkOrder.objects.create(title='Third', description='Three', category='Maintenance', priority='low', status='closed', created_by=self.user)

        self.client.force_login(self.user)
        response = self.client.get(reverse('workorders:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Work Orders')
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
