from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaveRequestViewSet, SubstituteViewSet,
UnitHeadReviewViewSet, EstablishmentVerificationViewSet,
DirectorSanctionViewSet, ImmediateWithdrawalViewSet

router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'substitutes', SubstituteViewSet)
router.register(r'unit-head-reviews', UnitHeadReviewViewSet)
router.register(r'establishment-verifications',
EstablishmentVerificationViewSet)
router.register(r'director-sanctions',
DirectorSanctionViewSet)
router.register(r'immediate-withdrawals',
ImmediateWithdrawalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]