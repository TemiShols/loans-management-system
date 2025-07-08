from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import LoanApplication


class LoanTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='john', email='john@test.com', password='pass123456')
        self.admin = User.objects.create_superuser(username='admin', email='admin@test.com', password='admin123')

    def test_fraud_detection_high_amount(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/loans/apply/', {
            "amount_requested": 6000000,
            "purpose": "Buy house"
        })
        self.assertEqual(response.status_code, 201)
        loan = LoanApplication.objects.get(user=self.user)
        self.assertEqual(loan.status, 'flagged')

    def test_successful_loan_application(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/loans/apply/', {
            "amount_requested": 200000,
            "purpose": "Tuition"
        })
        self.assertEqual(response.status_code, 201)
        loan = LoanApplication.objects.get(user=self.user)
        self.assertEqual(loan.status, 'pending')

    def test_flagged_loans_due_to_multiple_reasons(self):
        self.client.force_authenticate(user=self.user)

        # Create 4 recent loans
        for _ in range(4):
            LoanApplication.objects.create(user=self.user, amount_requested=1000)

        response = self.client.post('/api/loans/apply/', {
            "amount_requested": 6000000,
            "purpose": "Luxury"
        })
        self.assertEqual(response.status_code, 201)
        loan = LoanApplication.objects.get(user=self.user, amount_requested=6000000)
        self.assertEqual(loan.status, 'flagged')
        self.assertTrue(loan.fraud_flags.count() >= 2)
