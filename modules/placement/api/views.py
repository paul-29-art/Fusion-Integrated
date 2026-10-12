from rest_framework import viewsets, status, mixins,
permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import LeaveRequest, Substitute,
UnitHeadReview, EstablishmentVerification, DirectorSanction
from .serializers import LeaveRequestSerializer,
SubstituteSerializer, UnitHeadReviewSerializer,
EstablishmentVerificationSerializer,
DirectorSanctionSerializer
from django.contrib.auth.decorators import login_required

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def apply_leave(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'applied'
        leave_request.save()
        return Response({'message': 'Leave application successful'}, status=status.HTTP_200_OK)

class SubstituteViewSet(viewsets.ModelViewSet):
    queryset = Substitute.objects.all()
    serializer_class = SubstituteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        substitute = self.get_object()
        substitute.accepted = True
        substitute.save()
        return Response({'message': 'Substitute accepted'},
status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        substitute = self.get_object()
        substitute.accepted = False
        substitute.save()
        return Response({'message': 'Substitute declined'},
status=status.HTTP_200_OK)

class UnitHeadReviewViewSet(viewsets.ModelViewSet):
    queryset = UnitHeadReview.objects.all()
    serializer_class = UnitHeadReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def final_sanction(self, request, pk=None):
        review = self.get_object()
        review.final_sanction =
request.data.get('final_sanction', False)
        review.recommended = request.data.get('recommended',
None)
        review.save()
        return Response({'message': 'Final sanction processed'}, status=status.HTTP_200_OK)

class
EstablishmentVerificationViewSet(viewsets.ModelViewSet):
    queryset = EstablishmentVerification.objects.all()
    serializer_class = EstablishmentVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        verification = self.get_object()
        verification.verified = True
        verification.save()
        return Response({'message': 'Establishment verified'}, status=status.HTTP_200_OK)

class DirectorSanctionViewSet(viewsets.ModelViewSet):
    queryset = DirectorSanction.objects.all()
    serializer_class = DirectorSanctionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def sanction(self, request, pk=None):
        sanction = self.get_object()
        sanction.sanctioned = True
        sanction.save()
        return Response({'message': 'Sanction processed'},status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unsanction(self, request, pk=None):
        sanction = self.get_object()
        sanction.sanctioned = False
        sanction.save()
        return Response({'message': 'Unsanction processed'},status=status.HTTP_200_OK)

class ImmediateWithdrawalViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'withdrawn'
        leave_request.save()
        return Response({'message': 'Leave request withdrawn'}, status=status.HTTP_200_OK)