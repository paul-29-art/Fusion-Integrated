from django.urls import path, include
from rest_framework.routers import DefaultRouter
from modules.placement.api.views import (
    LeaveRequestViewSet,
    SubstituteViewSet,
    UnitHeadReviewViewSet,
    EstablishmentVerificationViewSet,
    DirectorSanctionViewSet,
    ImmediateWithdrawalViewSet,
    LeaveCategoryViewSet,
    LeaveBalanceViewSet,
    StationViewSet,
    HolidayViewSet,
)

router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'substitutes', SubstituteViewSet, basename='substitute')
router.register(r'unit-head-reviews', UnitHeadReviewViewSet, basename='unit-head-review')
router.register(r'establishment-verifications', EstablishmentVerificationViewSet, basename='establishment-verification')
router.register(r'director-sanctions', DirectorSanctionViewSet, basename='director-sanction')
router.register(r'immediate-withdrawals', ImmediateWithdrawalViewSet, basename='immediate-withdrawal')
router.register(r'leave-categories', LeaveCategoryViewSet, basename='leave-category')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leave-balance')
router.register(r'stations', StationViewSet, basename='station')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    # Direct frontend endpoints for ELM UI compatibility
    path('apply/', LeaveRequestViewSet.as_view({'post': 'apply'}), name='elm-apply'),
    path('leave-balance/', LeaveBalanceViewSet.as_view({'get': 'list'}), name='elm-leave-balance'),
    path('request-history/', LeaveRequestViewSet.as_view({'get': 'request_history'}), name='elm-request-history'),
    path('pending-requests/', LeaveRequestViewSet.as_view({'get': 'pending_requests'}), name='elm-pending-requests'),
    path('requests/<int:pk>/approve/', LeaveRequestViewSet.as_view({'post': 'approve'}), name='elm-request-approve'),
    path('requests/<int:pk>/reject/', LeaveRequestViewSet.as_view({'post': 'reject'}), name='elm-request-reject'),

    # Default router endpoints
    path('', include(router.urls)),
]