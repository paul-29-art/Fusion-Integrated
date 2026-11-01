from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from ..models import ResearchProposal, ConsultancyProject, FinancialRequest

User = get_user_model()


class RSPCTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='faculty_user', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_proposal_lifecycle(self):
        response = self.client.post('/api/rspc/proposals/', {
            'title': 'AI Edge Computing Study',
            'sponsor_agency': 'SERB / DST',
            'budget': '1250000.00',
            'duration_months': 24,
            'abstract': 'Study on low-latency inference on edge nodes.'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'SUBMITTED')

        proposal_id = response.data['id']
        approve_resp = self.client.post(f'/api/rspc/proposals/{proposal_id}/approve/', {'action': 'hod_approve'})
        self.assertEqual(approve_resp.status_code, 200)
        self.assertEqual(approve_resp.data['status'], 'HOD_APPROVED')

    def test_consultancy_revenue_share(self):
        consultancy = ConsultancyProject.objects.create(
            title='Smart Grid Optimization',
            pi=self.user,
            client_name='PowerGrid Corp',
            total_cost=Decimal('100000.00')
        )
        self.assertEqual(consultancy.institutional_share, Decimal('30000.00'))
        self.assertEqual(consultancy.investigator_share, Decimal('70000.00'))

    def test_financial_request_threshold(self):
        proposal = ResearchProposal.objects.create(
            title='Test Proposal', pi=self.user, sponsor_agency='ISRO', budget=Decimal('1000000.00')
        )
        req = FinancialRequest.objects.create(
            proposal=proposal, request_type='PROCUREMENT', amount=Decimal('600000.00'), justification='Workstation'
        )
        self.assertTrue(req.requires_director_approval)
