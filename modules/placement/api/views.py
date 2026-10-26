from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

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
from .serializers import (
    LeaveCategorySerializer,
    StationSerializer,
    HolidaySerializer,
    LeaveBalanceSerializer,
    LeaveRequestSerializer,
    SubstituteSerializer,
    UnitHeadReviewSerializer,
    EstablishmentVerificationSerializer,
    DirectorSanctionSerializer,
)


def deduct_leave_balance(leave_request):
    """Deduct days from user's leave balance when a leave request is approved."""
    try:
        leave_balance = LeaveBalance.objects.get(
            user=leave_request.user,
            category=leave_request.category
        )
        duration = leave_request.duration_in_days
        leave_balance.balance = max(0.0, leave_balance.balance - duration)
        leave_balance.save()
    except LeaveBalance.DoesNotExist:
        pass


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-created_at')
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        substitute_user = serializer.validated_data.get('substitute')
        initial_status = 'AWAITING_SUBSTITUTE' if substitute_user else 'AWAITING_UNIT_HEAD_REVIEW'
        instance = serializer.save(user=user, status=initial_status)

        if substitute_user:
            Substitute.objects.create(
                leave_request=instance,
                substitute_user=substitute_user,
                accepted=False
            )

    @action(detail=True, methods=['post'])
    def apply_leave(self, request, pk=None):
        leave_request = self.get_object()
        if leave_request.substitute:
            leave_request.status = 'AWAITING_SUBSTITUTE'
        else:
            leave_request.status = 'AWAITING_UNIT_HEAD_REVIEW'
        leave_request.save()
        return Response(
            {'message': 'Leave application submitted successfully', 'status': leave_request.status},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        leave_request = self.get_object()
        if leave_request.status in ['APPROVED', 'WITHDRAWN']:
            return Response(
                {'error': f'Cannot withdraw leave request in {leave_request.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        leave_request.status = 'WITHDRAWN'
        leave_request.save()
        return Response(
            {'message': 'Leave request withdrawn successfully', 'status': leave_request.status},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'APPROVED'
        leave_request.save()
        deduct_leave_balance(leave_request)
        return Response(
            {'message': 'Leave request approved successfully', 'status': leave_request.status},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'REJECTED'
        leave_request.save()
        return Response(
            {'message': 'Leave request rejected', 'status': leave_request.status},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='pending-requests')
    def pending_requests(self, request):
        pending_statuses = [
            'PENDING',
            'AWAITING_SUBSTITUTE',
            'AWAITING_UNIT_HEAD_REVIEW',
            'AWAITING_ESTABLISHMENT_ROUTING',
            'AWAITING_FINAL_SANCTION',
        ]
        requests = self.get_queryset().filter(status__in=pending_statuses)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='request-history')
    def request_history(self, request):
        user = request.user
        if user.is_authenticated and not user.is_staff:
            requests = self.get_queryset().filter(user=user)
        else:
            requests = self.get_queryset()
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='apply')
    def apply(self, request):
        user = request.user if request.user.is_authenticated else User.objects.first()
        category_val = request.data.get('category')
        start_date = request.data.get('startDate') or request.data.get('start_date')
        end_date = request.data.get('endDate') or request.data.get('end_date')
        station_leave = request.data.get('stationLeave', False)
        substitute_val = request.data.get('substitute')
        reason = request.data.get('reason', '')

        # Resolve category
        category = None
        if category_val:
            if isinstance(category_val, int) or (isinstance(category_val, str) and category_val.isdigit()):
                category = LeaveCategory.objects.filter(id=int(category_val)).first()
            else:
                category = LeaveCategory.objects.filter(name__iexact=str(category_val)).first()
                if not category:
                    category = LeaveCategory.objects.create(name=str(category_val), days=30.0)

        # Resolve substitute
        substitute_user = None
        if substitute_val:
            if isinstance(substitute_val, int) or (isinstance(substitute_val, str) and substitute_val.isdigit()):
                substitute_user = User.objects.filter(id=int(substitute_val)).first()
            else:
                substitute_user = User.objects.filter(username__iexact=str(substitute_val)).first()

        initial_status = 'AWAITING_SUBSTITUTE' if substitute_user else 'AWAITING_UNIT_HEAD_REVIEW'

        leave_request = LeaveRequest.objects.create(
            user=user,
            category=category,
            start_date=start_date,
            end_date=end_date,
            station_leave=bool(station_leave),
            substitute=substitute_user,
            status=initial_status,
            reason=reason,
        )

        if substitute_user:
            Substitute.objects.create(
                leave_request=leave_request,
                substitute_user=substitute_user,
                accepted=False
            )

        serializer = self.get_serializer(leave_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubstituteViewSet(viewsets.ModelViewSet):
    queryset = Substitute.objects.all().order_by('-created_at')
    serializer_class = SubstituteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        substitute = self.get_object()
        substitute.accepted = True
        substitute.remarks = request.data.get('remarks', substitute.remarks)
        substitute.save()

        leave_request = substitute.leave_request
        leave_request.status = 'AWAITING_UNIT_HEAD_REVIEW'
        leave_request.save()

        return Response(
            {
                'message': 'Substitute accepted successfully',
                'status': leave_request.status
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        substitute = self.get_object()
        substitute.accepted = False
        substitute.remarks = request.data.get('remarks', substitute.remarks)
        substitute.save()

        leave_request = substitute.leave_request
        leave_request.status = 'REJECTED'
        leave_request.save()

        return Response(
            {
                'message': 'Substitute declined',
                'status': leave_request.status
            },
            status=status.HTTP_200_OK
        )


class UnitHeadReviewViewSet(viewsets.ModelViewSet):
    queryset = UnitHeadReview.objects.all().order_by('-created_at')
    serializer_class = UnitHeadReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def final_sanction(self, request, pk=None):
        review = self.get_object()
        final_sanction = request.data.get('final_sanction', False)
        recommended = request.data.get('recommended', True)
        remarks = request.data.get('remarks', review.remarks)

        review.final_sanction = final_sanction
        review.recommended = recommended
        review.remarks = remarks
        review.save()

        leave_request = review.leave_request
        if recommended:
            if final_sanction:
                leave_request.status = 'APPROVED'
                deduct_leave_balance(leave_request)
            else:
                leave_request.status = 'AWAITING_ESTABLISHMENT_ROUTING'
        else:
            leave_request.status = 'REJECTED'
        leave_request.save()

        return Response(
            {
                'message': 'Final sanction processed',
                'status': leave_request.status
            },
            status=status.HTTP_200_OK
        )


class EstablishmentVerificationViewSet(viewsets.ModelViewSet):
    queryset = EstablishmentVerification.objects.all().order_by('-created_at')
    serializer_class = EstablishmentVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        verification = self.get_object()
        verified = request.data.get('verified', True)
        remarks = request.data.get('remarks', verification.remarks)

        verification.verified = verified
        verification.remarks = remarks
        verification.save()

        leave_request = verification.leave_request
        if verified:
            leave_request.status = 'AWAITING_FINAL_SANCTION'
        else:
            leave_request.status = 'REJECTED'
        leave_request.save()

        return Response(
            {
                'message': 'Establishment verification completed',
                'status': leave_request.status
            },
            status=status.HTTP_200_OK
        )


class DirectorSanctionViewSet(viewsets.ModelViewSet):
    queryset = DirectorSanction.objects.all().order_by('-created_at')
    serializer_class = DirectorSanctionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def sanction(self, request, pk=None):
        director_sanction = self.get_object()
        director_sanction.sanctioned = True
        director_sanction.remarks = request.data.get('remarks', director_sanction.remarks)
        director_sanction.save()

        leave_request = director_sanction.leave_request
        leave_request.status = 'APPROVED'
        leave_request.save()
        deduct_leave_balance(leave_request)

        return Response(
            {
                'message': 'Director sanction approved',
                'status': leave_request.status
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def unsanction(self, request, pk=None):
        director_sanction = self.get_object()
        director_sanction.sanctioned = False
        director_sanction.remarks = request.data.get('remarks', director_sanction.remarks)
        director_sanction.save()

        leave_request = director_sanction.leave_request
        leave_request.status = 'REJECTED'
        leave_request.save()

        return Response(
            {
                'message': 'Director sanction rejected/unsanctioned',
                'status': leave_request.status
            },
            status=status.HTTP_200_OK
        )


class ImmediateWithdrawalViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        leave_request = self.get_object()
        if leave_request.status in ['APPROVED', 'WITHDRAWN']:
            return Response(
                {'error': f'Cannot withdraw leave request in {leave_request.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        leave_request.status = 'WITHDRAWN'
        leave_request.save()
        return Response(
            {'message': 'Leave request withdrawn', 'status': leave_request.status},
            status=status.HTTP_200_OK
        )


class LeaveCategoryViewSet(viewsets.ModelViewSet):
    queryset = LeaveCategory.objects.all()
    serializer_class = LeaveCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return LeaveBalance.objects.filter(user=user)
        return LeaveBalance.objects.all()


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]