from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewSet,
    ResearchProposalViewSet,
    ConsultancyProjectViewSet,
    ConsultancyMilestoneViewSet,
    StaffAppointmentRequestViewSet,
    FinancialRequestViewSet,
    ProcurementRequestViewSet,
    ProjectReportViewSet,
    ProjectClosureViewSet,
    AuditLogViewSet,
    NotificationViewSet,
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'proposals', ResearchProposalViewSet, basename='proposal')
router.register(r'consultancies', ConsultancyProjectViewSet, basename='consultancy')
router.register(r'milestones', ConsultancyMilestoneViewSet, basename='milestone')
router.register(r'staff-appointments', StaffAppointmentRequestViewSet, basename='staff-appointment')
router.register(r'financial-requests', FinancialRequestViewSet, basename='financial-request')
router.register(r'procurements', ProcurementRequestViewSet, basename='procurement')
router.register(r'reports', ProjectReportViewSet, basename='report')
router.register(r'closures', ProjectClosureViewSet, basename='closure')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
