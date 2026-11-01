from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..models import ResearchProposal, ConsultancyProject, FinancialRequest, ProjectReport
from .serializers import (
    ResearchProposalSerializer,
    ConsultancyProjectSerializer,
    FinancialRequestSerializer,
    ProjectReportSerializer,
)

User = get_user_model()


class ResearchProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ResearchProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ResearchProposal.objects.all().order_by('-created_at')
        return ResearchProposal.objects.filter(pi=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(pi=self.request.user, status='SUBMITTED')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        proposal = self.get_object()
        action_type = request.data.get('action')
        reason = request.data.get('reason', '')

        if action_type == 'hod_approve':
            proposal.status = 'HOD_APPROVED'
        elif action_type == 'dean_approve':
            proposal.status = 'DEAN_APPROVED'
        elif action_type == 'reject':
            proposal.status = 'REJECTED'
            proposal.rejection_reason = reason
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.save()
        return Response(self.get_serializer(proposal).data)


class ConsultancyProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultancyProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ConsultancyProject.objects.all().order_by('-created_at')
        return ConsultancyProject.objects.filter(pi=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(pi=self.request.user)


class FinancialRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinancialRequest.objects.all().order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'approve':
            req.status = 'APPROVED'
        elif action_type == 'reject':
            req.status = 'REJECTED'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        req.save()
        return Response(self.get_serializer(req).data)


class ProjectReportViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectReport.objects.all().order_by('-submitted_at')
