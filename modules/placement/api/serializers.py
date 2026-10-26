from rest_framework import serializers
from django.contrib.auth.models import User
from modules.placement.models import (
    LeaveCategory,
    Station,
    Holiday,
    LeaveBalance,
    LeaveRequest,
    Substitute,
    UnitHeadReview,
    EstablishmentVerification,
    DirectorSanction,
)


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class LeaveCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveCategory
        fields = '__all__'


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = instance.category.name if instance.category else ''
        return data


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    substitute_name = serializers.CharField(source='substitute.username', read_only=True)
    startDate = serializers.DateField(source='start_date', read_only=True)
    endDate = serializers.DateField(source='end_date', read_only=True)
    duration = serializers.IntegerField(source='duration_in_days', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['employee'] = instance.user.username if instance.user else ''
        data['category'] = instance.category.name if instance.category else ''
        data['startDate'] = str(instance.start_date) if instance.start_date else ''
        data['endDate'] = str(instance.end_date) if instance.end_date else ''
        return data


class SubstituteSerializer(serializers.ModelSerializer):
    substitute_username = serializers.CharField(source='substitute_user.username', read_only=True)
    leave_request_details = LeaveRequestSerializer(source='leave_request', read_only=True)

    class Meta:
        model = Substitute
        fields = '__all__'


class UnitHeadReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    leave_request_details = LeaveRequestSerializer(source='leave_request', read_only=True)

    class Meta:
        model = UnitHeadReview
        fields = '__all__'


class EstablishmentVerificationSerializer(serializers.ModelSerializer):
    verifier_username = serializers.CharField(source='verified_by.username', read_only=True)
    leave_request_details = LeaveRequestSerializer(source='leave_request', read_only=True)

    class Meta:
        model = EstablishmentVerification
        fields = '__all__'


class DirectorSanctionSerializer(serializers.ModelSerializer):
    sanctioner_username = serializers.CharField(source='sanctioned_by.username', read_only=True)
    leave_request_details = LeaveRequestSerializer(source='leave_request', read_only=True)

    class Meta:
        model = DirectorSanction
        fields = '__all__'