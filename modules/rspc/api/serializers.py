from rest_framework import serializers
from ..models import ResearchProposal, ConsultancyProject, FinancialRequest, ProjectReport


class ResearchProposalSerializer(serializers.ModelSerializer):
    pi_username = serializers.CharField(source='pi.username', read_only=True)

    class Meta:
        model = ResearchProposal
        fields = '__all__'
        read_only_fields = ('id', 'pi', 'status', 'rejection_reason', 'created_at', 'updated_at')


class ConsultancyProjectSerializer(serializers.ModelSerializer):
    pi_username = serializers.CharField(source='pi.username', read_only=True)

    class Meta:
        model = ConsultancyProject
        fields = '__all__'
        read_only_fields = ('id', 'pi', 'institutional_share', 'investigator_share', 'created_at')


class FinancialRequestSerializer(serializers.ModelSerializer):
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)

    class Meta:
        model = FinancialRequest
        fields = '__all__'
        read_only_fields = ('id', 'requires_director_approval', 'status', 'created_at')


class ProjectReportSerializer(serializers.ModelSerializer):
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)

    class Meta:
        model = ProjectReport
        fields = '__all__'
        read_only_fields = ('id', 'status', 'submitted_at')
