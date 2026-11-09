from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (
    UserProfile,
    ResearchProposal,
    ConsultancyProject,
    ConsultancyMilestone,
    StaffAppointmentRequest,
    FinancialRequest,
    ProcurementRequest,
    ProjectReport,
    ProjectClosure,
    ReviewDecision,
    AuditLog,
    Notification,
)
from ..permissions import (
    get_user_rspc_role,
    IsFaculty,
    IsHoD,
    IsRSPCAdmin,
    IsDeanRSPC,
    IsDirector,
    IsOwnerOrElevatedRole,
)
from .serializers import (
    UserProfileSerializer,
    ResearchProposalSerializer,
    ConsultancyProjectSerializer,
    ConsultancyMilestoneSerializer,
    StaffAppointmentRequestSerializer,
    FinancialRequestSerializer,
    ProcurementRequestSerializer,
    ProjectReportSerializer,
    ProjectClosureSerializer,
    ReviewDecisionSerializer,
    AuditLogSerializer,
    NotificationSerializer,
)

User = get_user_model()


def record_audit(action_name, entity_type, entity_id, user, details=None):
    AuditLog.objects.create(
        action=action_name,
        entity_type=entity_type,
        entity_id=entity_id,
        user=user if user and user.is_authenticated else None,
        details=details or {},
    )


def create_notification(recipient, title, message, category='GENERAL', link=''):
    if recipient:
        Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            category=category,
            link=link,
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)

    @action(detail=False, methods=['post'])
    def switch_role(self, request):
        new_role = request.data.get('role')
        if new_role not in ['FACULTY', 'HOD', 'RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.role = new_role
        profile.save()
        record_audit('ROLE_SWITCH', 'USER', request.user.id, request.user, {'new_role': new_role})
        return Response(UserProfileSerializer(profile).data)


class ResearchProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ResearchProposalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrElevatedRole]

    def get_queryset(self):
        user = self.request.user
        role = get_user_rspc_role(user, self.request)
        if role in ['HOD', 'RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return ResearchProposal.objects.all().order_by('-created_at')
        return ResearchProposal.objects.filter(pi=user).order_by('-created_at')

    def perform_create(self, serializer):
        proposal = serializer.save(pi=self.request.user, status='DRAFT')
        record_audit('CREATE_PROPOSAL', 'RESEARCH_PROPOSAL', proposal.id, self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        proposal = self.get_object()
        if proposal.status != 'DRAFT':
            return Response({'error': 'Only draft proposals can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mandatory fields validation (BR-RSPC-013)
        if not proposal.title or not proposal.budget or not proposal.sponsor_agency or not proposal.objectives:
            return Response({'error': 'Mandatory proposal fields are incomplete (BR-RSPC-013).'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.status = 'SUBMITTED'
        proposal.submission_date = timezone.now()
        proposal.save()

        record_audit('SUBMIT_PROPOSAL', 'RESEARCH_PROPOSAL', proposal.id, request.user)
        create_notification(
            proposal.pi,
            "Proposal Submitted",
            f"Your proposal '{proposal.title}' has been submitted and routed to HoD.",
            category='PROPOSAL',
        )
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=['post'])
    def hod_review(self, request, pk=None):
        proposal = self.get_object()
        action_type = request.data.get('action')  # 'recommend' or 'reject'
        remarks = request.data.get('remarks', '')

        if action_type == 'recommend':
            proposal.status = 'HOD_RECOMMENDED'
            decision_code = 'RECOMMENDED'
        elif action_type == 'reject':
            proposal.status = 'HOD_REJECTED'
            decision_code = 'NOT_RECOMMENDED'
        else:
            return Response({'error': 'Invalid HoD review action.'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.save()
        ReviewDecision.objects.create(
            entity_type='PROPOSAL',
            entity_id=proposal.id,
            reviewer=request.user,
            reviewer_role='HOD',
            decision=decision_code,
            remarks=remarks,
        )
        record_audit('HOD_REVIEW', 'RESEARCH_PROPOSAL', proposal.id, request.user, {'action': action_type, 'remarks': remarks})
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=['post'])
    def admin_verify(self, request, pk=None):
        proposal = self.get_object()
        action_type = request.data.get('action')  # 'verify' or 'reject'
        remarks = request.data.get('remarks', '')

        if action_type == 'verify':
            proposal.status = 'ADMIN_VERIFIED'
            decision_code = 'VERIFIED'
        elif action_type == 'reject':
            proposal.status = 'ADMIN_REJECTED'
            decision_code = 'NOT_ELIGIBLE'
        else:
            return Response({'error': 'Invalid Admin verify action.'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.save()
        ReviewDecision.objects.create(
            entity_type='PROPOSAL',
            entity_id=proposal.id,
            reviewer=request.user,
            reviewer_role='RSPC_ADMIN',
            decision=decision_code,
            remarks=remarks,
        )
        record_audit('ADMIN_VERIFY', 'RESEARCH_PROPOSAL', proposal.id, request.user, {'action': action_type, 'remarks': remarks})
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=['post'])
    def dean_decide(self, request, pk=None):
        proposal = self.get_object()
        action_type = request.data.get('action')  # 'approve', 'reject', 'forward_director'
        remarks = request.data.get('remarks', '')

        if action_type == 'approve':
            proposal.status = 'DEAN_APPROVED'
            proposal.is_sanctioned = True
            proposal.sanctioned_budget = proposal.budget
            decision_code = 'APPROVED'
        elif action_type == 'reject':
            proposal.status = 'DEAN_REJECTED'
            decision_code = 'REJECTED'
        elif action_type == 'forward_director':
            proposal.status = 'FORWARDED_TO_DIRECTOR'
            decision_code = 'FORWARDED'
        else:
            return Response({'error': 'Invalid Dean decision action.'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.save()
        ReviewDecision.objects.create(
            entity_type='PROPOSAL',
            entity_id=proposal.id,
            reviewer=request.user,
            reviewer_role='DEAN_RSPC',
            decision=decision_code,
            remarks=remarks,
        )
        record_audit('DEAN_DECIDE', 'RESEARCH_PROPOSAL', proposal.id, request.user, {'action': action_type, 'remarks': remarks})
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=['post'])
    def director_decide(self, request, pk=None):
        proposal = self.get_object()
        action_type = request.data.get('action')  # 'approve' or 'reject'
        remarks = request.data.get('remarks', '')

        if action_type == 'approve':
            proposal.status = 'DIRECTOR_APPROVED'
            proposal.is_sanctioned = True
            proposal.sanctioned_budget = proposal.budget
            decision_code = 'APPROVED'
        elif action_type == 'reject':
            proposal.status = 'DIRECTOR_REJECTED'
            decision_code = 'REJECTED'
        else:
            return Response({'error': 'Invalid Director decision action.'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.save()
        ReviewDecision.objects.create(
            entity_type='PROPOSAL',
            entity_id=proposal.id,
            reviewer=request.user,
            reviewer_role='DIRECTOR',
            decision=decision_code,
            remarks=remarks,
        )
        record_audit('DIRECTOR_DECIDE', 'RESEARCH_PROPOSAL', proposal.id, request.user, {'action': action_type, 'remarks': remarks})
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=['get'])
    def decisions(self, request, pk=None):
        proposal = self.get_object()
        decisions = ReviewDecision.objects.filter(entity_type='PROPOSAL', entity_id=proposal.id).order_by('timestamp')
        return Response(ReviewDecisionSerializer(decisions, many=True).data)


class ConsultancyProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultancyProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrElevatedRole]

    def get_queryset(self):
        user = self.request.user
        role = get_user_rspc_role(user, self.request)
        if role in ['HOD', 'RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return ConsultancyProject.objects.all().order_by('-created_at')
        return ConsultancyProject.objects.filter(pi=user).order_by('-created_at')

    def perform_create(self, serializer):
        consultancy = serializer.save(pi=self.request.user, status='DRAFT')
        record_audit('CREATE_CONSULTANCY', 'CONSULTANCY_PROJECT', consultancy.id, self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        consultancy = self.get_object()
        consultancy.status = 'SUBMITTED'
        consultancy.save()
        record_audit('SUBMIT_CONSULTANCY', 'CONSULTANCY_PROJECT', consultancy.id, request.user)
        return Response(self.get_serializer(consultancy).data)

    @action(detail=True, methods=['post'])
    def hod_review(self, request, pk=None):
        consultancy = self.get_object()
        action_type = request.data.get('action')
        remarks = request.data.get('remarks', '')
        if action_type == 'recommend':
            consultancy.status = 'HOD_RECOMMENDED'
        else:
            consultancy.status = 'HOD_REJECTED'
        consultancy.save()
        ReviewDecision.objects.create(
            entity_type='CONSULTANCY', entity_id=consultancy.id, reviewer=request.user,
            reviewer_role='HOD', decision=action_type.upper(), remarks=remarks,
        )
        return Response(self.get_serializer(consultancy).data)

    @action(detail=True, methods=['post'])
    def admin_verify(self, request, pk=None):
        consultancy = self.get_object()
        action_type = request.data.get('action')
        remarks = request.data.get('remarks', '')
        if action_type == 'verify':
            consultancy.status = 'ADMIN_VERIFIED'
        else:
            consultancy.status = 'ADMIN_REJECTED'
        consultancy.save()
        ReviewDecision.objects.create(
            entity_type='CONSULTANCY', entity_id=consultancy.id, reviewer=request.user,
            reviewer_role='RSPC_ADMIN', decision=action_type.upper(), remarks=remarks,
        )
        return Response(self.get_serializer(consultancy).data)

    @action(detail=True, methods=['post'])
    def dean_decide(self, request, pk=None):
        consultancy = self.get_object()
        action_type = request.data.get('action')
        remarks = request.data.get('remarks', '')
        if action_type == 'approve':
            consultancy.status = 'DEAN_APPROVED'
        elif action_type == 'forward_director':
            consultancy.status = 'FORWARDED_TO_DIRECTOR'
        else:
            consultancy.status = 'DEAN_REJECTED'
        consultancy.save()
        ReviewDecision.objects.create(
            entity_type='CONSULTANCY', entity_id=consultancy.id, reviewer=request.user,
            reviewer_role='DEAN_RSPC', decision=action_type.upper(), remarks=remarks,
        )
        return Response(self.get_serializer(consultancy).data)

    @action(detail=True, methods=['post'])
    def director_decide(self, request, pk=None):
        consultancy = self.get_object()
        action_type = request.data.get('action')
        remarks = request.data.get('remarks', '')
        if action_type == 'approve':
            consultancy.status = 'DIRECTOR_APPROVED'
        else:
            consultancy.status = 'REJECTED'
        consultancy.save()
        ReviewDecision.objects.create(
            entity_type='CONSULTANCY', entity_id=consultancy.id, reviewer=request.user,
            reviewer_role='DIRECTOR', decision=action_type.upper(), remarks=remarks,
        )
        return Response(self.get_serializer(consultancy).data)


class ConsultancyMilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultancyMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ConsultancyMilestone.objects.all().order_by('due_date')

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        milestone = self.get_object()
        milestone.status = 'SUBMITTED'
        milestone.save()
        return Response(self.get_serializer(milestone).data)

    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        milestone = self.get_object()
        milestone.status = 'SETTLED'
        milestone.settlement_date = timezone.now().date()
        milestone.save()
        return Response(self.get_serializer(milestone).data)


class StaffAppointmentRequestViewSet(viewsets.ModelViewSet):
    serializer_class = StaffAppointmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = get_user_rspc_role(user, self.request)
        if role in ['RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return StaffAppointmentRequest.objects.all().order_by('-created_at')
        return StaffAppointmentRequest.objects.filter(faculty=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(faculty=self.request.user, status='REQUESTED')

    @action(detail=True, methods=['post'])
    def admin_verify(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'verify':
            req.status = 'ADMIN_VERIFIED'
        else:
            req.status = 'NOT_ELIGIBLE'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def record_selection(self, request, pk=None):
        req = self.get_object()
        req.selected_candidate_name = request.data.get('selected_candidate_name', '')
        req.selection_committee_remarks = request.data.get('selection_committee_remarks', '')
        req.selection_recommended_by_pi = True
        req.status = 'RECOMMENDATION_RECORDED'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def dean_decide(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'approve':
            req.status = 'DEAN_APPROVED'
        elif action_type == 'forward_director':
            req.status = 'FORWARDED_TO_DIRECTOR'
        else:
            req.status = 'REJECTED'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def director_decide(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'approve':
            req.status = 'APPROVED'
        else:
            req.status = 'REJECTED'
        req.save()
        return Response(self.get_serializer(req).data)


class FinancialRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = get_user_rspc_role(user, self.request)
        if role in ['RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return FinancialRequest.objects.all().order_by('-created_at')
        return FinancialRequest.objects.filter(faculty=user).order_by('-created_at')

    def perform_create(self, serializer):
        req = serializer.save(faculty=self.request.user, status='SUBMITTED')
        record_audit('SUBMIT_FINANCIAL_REQUEST', 'FINANCIAL_REQUEST', req.id, self.request.user)

    @action(detail=True, methods=['post'])
    def admin_verify(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'verify':
            req.status = 'VERIFIED'
            req.admin_verified_at = timezone.now()
        else:
            req.status = 'NOT_ELIGIBLE'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def dean_decide(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')

        if action_type == 'approve':
            if req.requires_director_approval:
                req.status = 'FORWARDED_TO_DIRECTOR'
            else:
                req.status = 'DEAN_APPROVED'
                if req.proposal:
                    req.proposal.expenditure_total += req.amount
                    req.proposal.save()
        elif action_type == 'forward_director':
            req.status = 'FORWARDED_TO_DIRECTOR'
        else:
            req.status = 'REJECTED'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def director_decide(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'approve':
            req.status = 'APPROVED'
            if req.proposal:
                req.proposal.expenditure_total += req.amount
                req.proposal.save()
        else:
            req.status = 'REJECTED'
        req.save()
        return Response(self.get_serializer(req).data)


class ProcurementRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ProcurementRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = get_user_rspc_role(user, self.request)
        if role in ['RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return ProcurementRequest.objects.all().order_by('-created_at')
        return ProcurementRequest.objects.filter(faculty=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(faculty=self.request.user, status='SUBMITTED')

    @action(detail=True, methods=['post'])
    def admin_verify(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'verify':
            req.status = 'VERIFIED'
        else:
            req.status = 'NOT_ELIGIBLE'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def dean_decide(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'approve':
            req.status = 'DEAN_APPROVED'
        elif action_type == 'forward_director':
            req.status = 'FORWARDED_TO_DIRECTOR'
        else:
            req.status = 'REJECTED'
        req.save()
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def director_decide(self, request, pk=None):
        req = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'approve':
            req.status = 'APPROVED'
        else:
            req.status = 'REJECTED'
        req.save()
        return Response(self.get_serializer(req).data)


class ProjectReportViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectReport.objects.all().order_by('-submitted_at')

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user, status='SUBMITTED')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        rep = self.get_object()
        rep.status = 'ACCEPTED'
        rep.save()
        return Response(self.get_serializer(rep).data)


class ProjectClosureViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectClosureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectClosure.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(faculty=self.request.user, status='SUBMITTED')

    @action(detail=True, methods=['post'])
    def admin_verify(self, request, pk=None):
        closure = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'verify':
            closure.financial_settlement_status = 'VERIFIED'
            closure.asset_declaration_verified = True
            closure.status = 'VERIFIED'
        else:
            closure.status = 'NOT_ELIGIBLE'
        closure.save()
        return Response(self.get_serializer(closure).data)

    @action(detail=True, methods=['post'])
    def dean_decide(self, request, pk=None):
        closure = self.get_object()
        action_type = request.data.get('action')
        remarks = request.data.get('remarks', '')
        closure.dean_remarks = remarks
        if action_type == 'approve':
            closure.status = 'ARCHIVED'
            closure.archived_at = timezone.now()
            closure.proposal.status = 'DIRECTOR_APPROVED'
        elif action_type == 'forward_director':
            closure.status = 'FORWARDED_TO_DIRECTOR'
        else:
            closure.status = 'REJECTED'
        closure.save()
        return Response(self.get_serializer(closure).data)

    @action(detail=True, methods=['post'])
    def director_decide(self, request, pk=None):
        closure = self.get_object()
        action_type = request.data.get('action')
        remarks = request.data.get('remarks', '')
        closure.director_remarks = remarks
        if action_type == 'approve':
            closure.status = 'ARCHIVED'
            closure.archived_at = timezone.now()
        else:
            closure.status = 'REJECTED'
        closure.save()
        return Response(self.get_serializer(closure).data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AuditLog.objects.all().order_by('-timestamp')


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'marked_as_read'})
