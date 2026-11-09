from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
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

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'department', 'designation')


class ReviewDecisionSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = ReviewDecision
        fields = ('id', 'entity_type', 'entity_id', 'reviewer', 'reviewer_username', 'reviewer_role', 'decision', 'remarks', 'timestamp')
        read_only_fields = ('id', 'reviewer', 'timestamp')


class ResearchProposalSerializer(serializers.ModelSerializer):
    pi_username = serializers.CharField(source='pi.username', read_only=True)
    remaining_balance = serializers.SerializerMethodField()

    class Meta:
        model = ResearchProposal
        fields = '__all__'
        read_only_fields = ('id', 'pi', 'is_sanctioned', 'sanctioned_budget', 'expenditure_total', 'submission_date', 'created_at', 'updated_at')

    def get_remaining_balance(self, obj):
        if obj.is_sanctioned and obj.sanctioned_budget:
            return float(obj.sanctioned_budget - obj.expenditure_total)
        return float(obj.budget - obj.expenditure_total)

    def validate_budget(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Budget must be greater than zero.")
        return value


class ConsultancyMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultancyMilestone
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class ConsultancyProjectSerializer(serializers.ModelSerializer):
    pi_username = serializers.CharField(source='pi.username', read_only=True)
    milestones = ConsultancyMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = ConsultancyProject
        fields = '__all__'
        read_only_fields = ('id', 'pi', 'institutional_share', 'investigator_share', 'created_at', 'updated_at')

    def validate_total_cost(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Total cost must be greater than zero.")
        return value


class StaffAppointmentRequestSerializer(serializers.ModelSerializer):
    faculty_username = serializers.CharField(source='faculty.username', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)
    consultancy_title = serializers.CharField(source='consultancy.title', read_only=True)

    class Meta:
        model = StaffAppointmentRequest
        fields = '__all__'
        read_only_fields = ('id', 'faculty', 'created_at')


class FinancialRequestSerializer(serializers.ModelSerializer):
    faculty_username = serializers.CharField(source='faculty.username', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)
    consultancy_title = serializers.CharField(source='consultancy.title', read_only=True)

    class Meta:
        model = FinancialRequest
        fields = '__all__'
        read_only_fields = ('id', 'faculty', 'requires_director_approval', 'admin_verified_at', 'created_at')

    def validate_amount(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Request amount must be greater than zero.")
        return value


class ProcurementRequestSerializer(serializers.ModelSerializer):
    faculty_username = serializers.CharField(source='faculty.username', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)

    class Meta:
        model = ProcurementRequest
        fields = '__all__'
        read_only_fields = ('id', 'faculty', 'sanctioned_budget_balance_checked', 'created_at')

    def validate_estimated_cost(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Estimated cost must be greater than zero.")
        return value


class ProjectReportSerializer(serializers.ModelSerializer):
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)

    class Meta:
        model = ProjectReport
        fields = '__all__'
        read_only_fields = ('id', 'submitted_by', 'submitted_at')


class ProjectClosureSerializer(serializers.ModelSerializer):
    faculty_username = serializers.CharField(source='faculty.username', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)

    class Meta:
        model = ProjectClosure
        fields = '__all__'
        read_only_fields = ('id', 'faculty', 'archived_at', 'created_at')


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ('id', 'action', 'entity_type', 'entity_id', 'user', 'username', 'timestamp', 'details')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'recipient', 'title', 'message', 'category', 'link', 'created_at')
