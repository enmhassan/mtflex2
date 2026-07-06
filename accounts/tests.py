from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='alice',
            email='alice@example.com',
            password='oldpass123',
        )

    def test_profile_page_allows_password_change(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('accounts:profile'), {
            'old_password': 'oldpass123',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!',
        })

        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))
