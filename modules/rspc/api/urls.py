from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ResearchProposalViewSet,
    ConsultancyProjectViewSet,
    FinancialRequestViewSet,
    ProjectReportViewSet,
)

router = DefaultRouter()
router.register(r'proposals', ResearchProposalViewSet, basename='proposal')
router.register(r'consultancies', ConsultancyProjectViewSet, basename='consultancy')
router.register(r'financial-requests', FinancialRequestViewSet, basename='financial-request')
router.register(r'reports', ProjectReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
